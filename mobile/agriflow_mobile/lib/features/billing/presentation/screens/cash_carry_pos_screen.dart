import 'package:agriflow_mobile/features/billing/domain/models/billing_models.dart';
import 'package:agriflow_mobile/features/billing/presentation/providers/billing_providers.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class CashCarryPosScreen extends ConsumerStatefulWidget {
  const CashCarryPosScreen({super.key});

  @override
  ConsumerState<CashCarryPosScreen> createState() => _CashCarryPosScreenState();
}

class _CashCarryPosScreenState extends ConsumerState<CashCarryPosScreen> {
  final _searchController = TextEditingController();
  final _customerNameController = TextEditingController();
  final _customerMobileController = TextEditingController();
  PaymentMode _paymentMode = PaymentMode.cash;
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    _customerNameController.dispose();
    _customerMobileController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cart = ref.watch(cartProvider);
    final total = ref.watch(cartTotalProvider);
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.cashCarryTitle),
        actions: [
          if (cart.isNotEmpty)
            TextButton(
              onPressed: () => ref.read(cartProvider.notifier).clear(),
              child: Text(
                l10n.cartClear,
                style: const TextStyle(color: Colors.white),
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: l10n.itemSearchHint,
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
            child: cart.isEmpty ? _buildEmptyCart(l10n) : _buildCartList(cart),
          ),
          if (cart.isNotEmpty) _buildBottomBar(l10n, total),
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
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('₹${item.standardRate.toStringAsFixed(2)}'),
                        const Icon(Icons.add_shopping_cart, color: Colors.green),
                      ],
                    ),
                    onTap: () {
                      ref.read(cartProvider.notifier).addItem(item);
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
          error: (e, _) => Center(child: Text(l10n.errorGeneric)),
        );
      },
    );
  }

  Widget _buildEmptyCart(AppLocalizations l10n) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.shopping_cart_outlined, size: 80, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            l10n.cartEmpty,
            style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
          ),
          const SizedBox(height: 8),
          Text(
            l10n.cartEmptyHint,
            style: TextStyle(color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }

  Widget _buildCartList(List<CartLine> cart) {
    return ListView.separated(
      itemCount: cart.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, i) {
        final line = cart[i];
        return ListTile(
          title: Text(line.item.name),
          subtitle: Text(
            '₹${line.rate.toStringAsFixed(2)} × ${line.qty.toStringAsFixed(0)} ${line.item.uom}',
          ),
          trailing: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                icon: const Icon(Icons.remove_circle, color: Colors.red),
                onPressed: () => ref
                    .read(cartProvider.notifier)
                    .updateQty(line.item.code, line.qty - 1),
              ),
              Text(
                line.qty.toStringAsFixed(0),
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              IconButton(
                icon: const Icon(Icons.add_circle, color: Colors.green),
                onPressed: () => ref
                    .read(cartProvider.notifier)
                    .updateQty(line.item.code, line.qty + 1),
              ),
              const SizedBox(width: 8),
              Text(
                '₹${line.amount.toStringAsFixed(2)}',
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildBottomBar(AppLocalizations l10n, double total) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.12),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${l10n.cartTotal}:',
                style: TextStyle(fontSize: 18, color: Colors.grey.shade700),
              ),
              Text(
                '₹${total.toStringAsFixed(2)}',
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            icon: const Icon(Icons.payments),
            label: Text(l10n.proceedToPayment),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
            ),
            onPressed: () => _showCheckoutSheet(context, l10n, total),
          ),
        ],
      ),
    );
  }

  void _showCheckoutSheet(
    BuildContext context,
    AppLocalizations l10n,
    double total,
  ) {
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
          children: [
            Text(
              l10n.customerDetailsTitle,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _customerNameController,
              decoration: InputDecoration(
                labelText: l10n.customerNameOptional,
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _customerMobileController,
              decoration: InputDecoration(
                labelText: l10n.customerMobileOptional,
                border: const OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
              maxLength: 10,
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
            Text(
              '${l10n.cartTotal}: ₹${total.toStringAsFixed(2)}',
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => _saveInvoice(ctx, l10n),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 0),
              ),
              child: Text(l10n.saveInvoice, style: const TextStyle(fontSize: 18)),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Future<void> _saveInvoice(BuildContext ctx, AppLocalizations l10n) async {
    final cart = ref.read(cartProvider);
    if (cart.isEmpty) return;

    showDialog<void>(
      context: ctx,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final repo = ref.read(billingRepositoryProvider);
      final result = await repo.createCashCarryInvoice(
        items: cart,
        customerName: _customerNameController.text.trim(),
        customerMobile: _customerMobileController.text.trim(),
        paymentMode: _paymentMode,
      );

      if (!ctx.mounted) return;
      Navigator.of(ctx).pop();
      Navigator.of(ctx).pop();

      ref.read(cartProvider.notifier).clear();
      _customerNameController.clear();
      _customerMobileController.clear();

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
              Text('${l10n.cartTotal}: ₹${result.total.toStringAsFixed(2)}'),
              Text(l10n.invoiceItemsCount(result.itemsCount)),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
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
