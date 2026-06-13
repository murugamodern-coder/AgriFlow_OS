import 'package:agriflow_mobile/features/billing/domain/models/billing_models.dart';
import 'package:agriflow_mobile/features/billing/domain/models/project_sale_models.dart';
import 'package:agriflow_mobile/features/billing/presentation/providers/billing_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ProjectSaleCartNotifier extends StateNotifier<ProjectSaleQuote?> {
  ProjectSaleCartNotifier() : super(null);

  void initFor(String projectName, String farmerName) {
    state = ProjectSaleQuote(
      projectName: projectName,
      farmerName: farmerName,
      items: const [],
    );
  }

  void addItem(CatalogItem item, {double qty = 1}) {
    final current = state;
    if (current == null) return;

    final existingIdx =
        current.items.indexWhere((c) => c.item.code == item.code);
    final newItems = List<CartLine>.from(current.items);

    if (existingIdx >= 0) {
      newItems[existingIdx] = CartLine(
        item: item,
        qty: newItems[existingIdx].qty + qty,
        rate: newItems[existingIdx].rate,
      );
    } else {
      newItems.add(CartLine(item: item, qty: qty, rate: item.standardRate));
    }

    state = current.copyWith(items: newItems).withAutoSplit();
  }

  void updateQty(String itemCode, double newQty) {
    final current = state;
    if (current == null) return;

    final List<CartLine> newItems;
    if (newQty <= 0) {
      newItems = current.items.where((c) => c.item.code != itemCode).toList();
    } else {
      newItems = current.items
          .map(
            (c) => c.item.code == itemCode
                ? CartLine(item: c.item, qty: newQty, rate: c.rate)
                : c,
          )
          .toList();
    }

    state = current.copyWith(items: newItems).withAutoSplit();
  }

  void updateSubsidySplit(double subsidy, double farmer) {
    final current = state;
    if (current == null) return;
    state = current.copyWith(
      subsidyAmount: subsidy,
      farmerPortion: farmer,
    );
  }

  void setPaymentMode(PaymentMode mode) {
    final current = state;
    if (current == null) return;
    state = current.copyWith(paymentMode: mode);
  }

  void clear() {
    state = null;
  }
}

final projectSaleCartProvider =
    StateNotifierProvider<ProjectSaleCartNotifier, ProjectSaleQuote?>(
  (ref) => ProjectSaleCartNotifier(),
);

final projectDetailsProvider =
    FutureProvider.family<Map<String, dynamic>, String>(
  (ref, projectName) async {
    final repo = ref.watch(billingRepositoryProvider);
    return repo.getProjectDetails(projectName);
  },
);
