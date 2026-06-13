import 'package:agriflow_mobile/features/billing/domain/models/billing_models.dart';
import 'package:agriflow_mobile/features/billing/domain/models/project_sale_models.dart';
import 'package:agriflow_mobile/features/billing/presentation/providers/billing_providers.dart';
import 'package:agriflow_mobile/features/billing/presentation/providers/project_sale_providers.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ProjectSaleScreen extends ConsumerStatefulWidget {
  const ProjectSaleScreen({super.key, required this.projectName});

  final String projectName;

  @override
  ConsumerState<ProjectSaleScreen> createState() => _ProjectSaleScreenState();
}

class _ProjectSaleScreenState extends ConsumerState<ProjectSaleScreen> {
  final _searchController = TextEditingController();
  final _subsidyController = TextEditingController();
  final _farmerPortionController = TextEditingController();
  String _searchQuery = '';
  PaymentMode _paymentMode = PaymentMode.cash;
  bool _initialized = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _initCart());
  }

  @override
  void dispose() {
    _searchController.dispose();
    _subsidyController.dispose();
    _farmerPortionController.dispose();
    super.dispose();
  }

  Future<void> _initCart() async {
    try {
      final project =
          await ref.read(projectDetailsProvider(widget.projectName).future);
      final farmerName = project['project_title'] as String? ??
          project['farmer'] as String? ??
          widget.projectName;
      ref
          .read(projectSaleCartProvider.notifier)
          .initFor(widget.projectName, farmerName);
      if (mounted) setState(() => _initialized = true);
    } catch (_) {
      ref.read(projectSaleCartProvider.notifier).initFor(
            widget.projectName,
            widget.projectName,
          );
      if (mounted) setState(() => _initialized = true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cart = ref.watch(projectSaleCartProvider);
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.projectSaleTitle(widget.projectName)),
        actions: [
          if (cart != null && cart.items.isNotEmpty)
            TextButton(
              onPressed: () =>
                  ref.read(projectSaleCartProvider.notifier).clear(),
              child: Text(
                l10n.cartClear,
                style: const TextStyle(color: Colors.white),
              ),
            ),
        ],
      ),
      body: !_initialized || cart == null
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                _buildProjectHeader(cart, l10n),
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: l10n.projectSaleSearchHint,
                      prefixIcon: const Icon(Icons.search),
                      border: const OutlineInputBorder(),
                      isDense: true,
                    ),
                    onChanged: (value) => setState(() => _searchQuery = value),
                  ),
                ),
                if (_searchQuery.isNotEmpty)
                  Expanded(flex: 1, child: _buildSearchResults(l10n)),
                Expanded(
                  flex: 2,
                  child: cart.items.isEmpty
                      ? _buildEmptyState(l10n)
                      : _buildQuotationList(cart.items),
                ),
                if (cart.items.isNotEmpty) _buildBottomSection(cart, l10n),
              ],
            ),
    );
  }

  Widget _buildProjectHeader(ProjectSaleQuote cart, AppLocalizations l10n) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      color: Colors.blue.withValues(alpha: 0.08),
      child: Row(
        children: [
          Icon(Icons.agriculture, color: Colors.blue.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  cart.farmerName,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  widget.projectName,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          Text(
            '₹${cart.totalAmount.toStringAsFixed(0)}',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchResults(AppLocalizations l10n) {
    return Consumer(
      builder: (context, ref, _) {
        final itemsAsync = ref.watch(itemSearchProvider(_searchQuery));
        return itemsAsync.when(
          data: (items) {
            if (items.isEmpty) {
              return Center(child: Text(l10n.noItemsFound));
            }
            return ColoredBox(
              color: Colors.grey.shade100,
              child: ListView.builder(
                itemCount: items.length,
                itemBuilder: (context, i) {
                  final item = items[i];
                  return ListTile(
                    title: Text(item.name),
                    subtitle: Text('${item.code} • ${item.uom}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('₹${item.standardRate.toStringAsFixed(0)}'),
                        const SizedBox(width: 8),
                        Icon(Icons.add_circle, color: Colors.green.shade700),
                      ],
                    ),
                    onTap: () {
                      ref.read(projectSaleCartProvider.notifier).addItem(item);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(l10n.itemAddedToCart(item.name)),
                          duration: const Duration(seconds: 1),
                        ),
                      );
                    },
                  );
                },
              ),
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(child: Text('${l10n.errorGeneric}: $e')),
        );
      },
    );
  }

  Widget _buildEmptyState(AppLocalizations l10n) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.description_outlined, size: 72, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            l10n.projectSaleEmptyHint,
            style: TextStyle(color: Colors.grey.shade600),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildQuotationList(List<CartLine> items) {
    return ListView.separated(
      itemCount: items.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, i) {
        final line = items[i];
        return ListTile(
          title: Text(line.item.name),
          subtitle: Text(
            '₹${line.rate.toStringAsFixed(0)} × ${line.qty.toStringAsFixed(0)} ${line.item.uom}',
          ),
          trailing: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                icon: Icon(Icons.remove_circle, color: Colors.red.shade700),
                onPressed: () => ref
                    .read(projectSaleCartProvider.notifier)
                    .updateQty(line.item.code, line.qty - 1),
              ),
              Text(
                line.qty.toStringAsFixed(0),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              IconButton(
                icon: Icon(Icons.add_circle, color: Colors.green.shade700),
                onPressed: () => ref
                    .read(projectSaleCartProvider.notifier)
                    .updateQty(line.item.code, line.qty + 1),
              ),
              const SizedBox(width: 8),
              Text(
                '₹${line.amount.toStringAsFixed(0)}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildBottomSection(ProjectSaleQuote cart, AppLocalizations l10n) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 4,
            offset: Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.amber.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  l10n.subsidySplit,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _splitTile(
                        l10n.govtSubsidy,
                        cart.subsidyAmount,
                        Colors.green,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _splitTile(
                        l10n.farmerPortion,
                        cart.farmerPortion,
                        Colors.orange,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(l10n.cartTotal, style: const TextStyle(fontSize: 18)),
              Text(
                '₹${cart.totalAmount.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            icon: const Icon(Icons.receipt_long),
            label: Text(l10n.generateInvoice),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 0),
            ),
            onPressed: () => _showConfirmSheet(cart, l10n),
          ),
        ],
      ),
    );
  }

  Widget _splitTile(String label, double amount, MaterialColor color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(fontSize: 11, color: color.shade700)),
          const SizedBox(height: 4),
          Text(
            '₹${amount.toStringAsFixed(0)}',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color.shade800,
            ),
          ),
        ],
      ),
    );
  }

  void _showConfirmSheet(ProjectSaleQuote cart, AppLocalizations l10n) {
    _subsidyController.text = cart.subsidyAmount.toStringAsFixed(0);
    _farmerPortionController.text = cart.farmerPortion.toStringAsFixed(0);
    _paymentMode = cart.paymentMode;

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(ctx).viewInsets.bottom,
          left: 16,
          right: 16,
          top: 16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              l10n.projectSaleConfirmTitle,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Text('${l10n.projectSaleProjectLabel}: ${widget.projectName}'),
            Text('${l10n.projectSaleFarmerLabel}: ${cart.farmerName}'),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _subsidyController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: l10n.govtSubsidyAmount,
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _farmerPortionController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: l10n.farmerPortionAmount,
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<PaymentMode>(
              value: _paymentMode,
              decoration: InputDecoration(
                labelText: l10n.paymentModeLabel,
                border: const OutlineInputBorder(),
              ),
              items: PaymentMode.values
                  .map(
                    (mode) => DropdownMenuItem(
                      value: mode,
                      child: Text(mode.label(l10n)),
                    ),
                  )
                  .toList(),
              onChanged: (v) => setState(() => _paymentMode = v ?? PaymentMode.cash),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => _generate(ctx, cart, l10n),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              child: Text(l10n.confirmGenerate),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Future<void> _generate(
    BuildContext ctx,
    ProjectSaleQuote cart,
    AppLocalizations l10n,
  ) async {
    final subsidy =
        double.tryParse(_subsidyController.text.trim()) ?? cart.subsidyAmount;
    final farmer =
        double.tryParse(_farmerPortionController.text.trim()) ?? cart.farmerPortion;

    if ((subsidy + farmer).round() != cart.totalAmount.round()) {
      ScaffoldMessenger.of(ctx).showSnackBar(
        SnackBar(
          content: Text(l10n.projectSaleSplitError(cart.totalAmount)),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    showDialog<void>(
      context: ctx,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final repo = ref.read(billingRepositoryProvider);
      final result = await repo.createProjectInvoice(
        projectName: widget.projectName,
        items: cart.items,
        subsidyAmount: subsidy,
        farmerPortion: farmer,
        paymentMode: _paymentMode,
      );

      if (!ctx.mounted) return;
      Navigator.of(ctx).pop();
      Navigator.of(ctx).pop();

      ref.read(projectSaleCartProvider.notifier).clear();

      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (_) => AlertDialog(
          icon: const Icon(Icons.check_circle, color: Colors.green, size: 64),
          title: Text(l10n.invoiceCreatedTitle),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(result.name, style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text('${l10n.cartTotal}: ₹${result.total.toStringAsFixed(0)}'),
              if (result.subsidyPortion != null)
                Text('${l10n.govtSubsidy}: ₹${result.subsidyPortion!.toStringAsFixed(0)}'),
              if (result.farmerPortion != null)
                Text('${l10n.farmerPortion}: ₹${result.farmerPortion!.toStringAsFixed(0)}'),
              Text(l10n.invoiceItemsCount(result.itemsCount)),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                context.pop();
              },
              child: Text(l10n.confirm),
            ),
          ],
        ),
      );
    } catch (e) {
      if (ctx.mounted) Navigator.of(ctx).pop();
      if (ctx.mounted) {
        ScaffoldMessenger.of(ctx).showSnackBar(
          SnackBar(
            content: Text('${l10n.errorGeneric}: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
