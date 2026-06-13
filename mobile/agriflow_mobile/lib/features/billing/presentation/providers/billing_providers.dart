import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/billing/data/billing_repository.dart';
import 'package:agriflow_mobile/features/billing/domain/models/billing_models.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final billingRepositoryProvider = Provider<BillingRepository>((ref) {
  return BillingRepository(
    dio: ref.watch(dioProvider),
    config: ref.watch(apiConfigProvider),
  );
});

class CartNotifier extends StateNotifier<List<CartLine>> {
  CartNotifier() : super([]);

  void addItem(CatalogItem item, {double qty = 1}) {
    final idx = state.indexWhere((c) => c.item.code == item.code);
    if (idx >= 0) {
      final updated = List<CartLine>.from(state);
      updated[idx] = CartLine(
        item: item,
        qty: updated[idx].qty + qty,
        rate: updated[idx].rate,
      );
      state = updated;
    } else {
      state = [
        ...state,
        CartLine(item: item, qty: qty, rate: item.standardRate),
      ];
    }
  }

  void updateQty(String itemCode, double newQty) {
    if (newQty <= 0) {
      state = state.where((c) => c.item.code != itemCode).toList();
      return;
    }
    state = state
        .map(
          (c) => c.item.code == itemCode
              ? CartLine(item: c.item, qty: newQty, rate: c.rate)
              : c,
        )
        .toList();
  }

  void updateRate(String itemCode, double newRate) {
    state = state
        .map(
          (c) => c.item.code == itemCode
              ? CartLine(item: c.item, qty: c.qty, rate: newRate)
              : c,
        )
        .toList();
  }

  void removeItem(String itemCode) {
    state = state.where((c) => c.item.code != itemCode).toList();
  }

  void clear() {
    state = [];
  }
}

final cartProvider =
    StateNotifierProvider<CartNotifier, List<CartLine>>((ref) {
  return CartNotifier();
});

final cartTotalProvider = Provider<double>((ref) {
  final cart = ref.watch(cartProvider);
  return cart.fold(0.0, (sum, c) => sum + c.amount);
});

final itemSearchProvider =
    FutureProvider.family<List<CatalogItem>, String>((ref, query) {
  final repo = ref.watch(billingRepositoryProvider);
  return repo.searchItems(search: query, limit: 30);
});
