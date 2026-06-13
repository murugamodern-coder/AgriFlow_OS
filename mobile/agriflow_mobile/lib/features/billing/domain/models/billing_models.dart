import 'package:agriflow_mobile/l10n/app_localizations.dart';

class CatalogItem {
  const CatalogItem({
    required this.code,
    required this.name,
    required this.uom,
    required this.standardRate,
    this.image,
  });

  final String code;
  final String name;
  final String uom;
  final double standardRate;
  final String? image;

  factory CatalogItem.fromJson(Map<String, dynamic> json) => CatalogItem(
        code: json['name'] as String,
        name: json['item_name'] as String,
        uom: json['stock_uom'] as String? ?? 'Nos',
        standardRate: (json['standard_rate'] as num?)?.toDouble() ?? 0.0,
        image: json['image'] as String?,
      );
}

class CartLine {
  CartLine({
    required this.item,
    required this.qty,
    required this.rate,
  });

  final CatalogItem item;
  double qty;
  double rate;

  double get amount => qty * rate;

  Map<String, dynamic> toApiPayload() => {
        'item_code': item.code,
        'qty': qty,
        'rate': rate,
      };
}

class InvoiceResult {
  const InvoiceResult({
    required this.name,
    required this.total,
    required this.itemsCount,
    this.subsidyPortion,
    this.farmerPortion,
    this.draft = false,
  });

  final String name;
  final double total;
  final int itemsCount;
  final double? subsidyPortion;
  final double? farmerPortion;
  final bool draft;

  factory InvoiceResult.fromJson(Map<String, dynamic> json) => InvoiceResult(
        name: json['name'] as String,
        total: (json['total'] as num).toDouble(),
        itemsCount: (json['items_count'] as int?) ?? 0,
      );

  factory InvoiceResult.fromProjectJson(
    Map<String, dynamic> json, {
    required int itemsCount,
  }) =>
      InvoiceResult(
        name: json['name'] as String,
        total: (json['total'] as num).toDouble(),
        itemsCount: itemsCount,
        subsidyPortion: (json['subsidy_portion'] as num?)?.toDouble(),
        farmerPortion: (json['farmer_portion'] as num?)?.toDouble(),
        draft: json['draft'] == true || json['draft'] == 1,
      );
}

enum PaymentMode { cash, upi, card, bankTransfer, mixed }

extension PaymentModeX on PaymentMode {
  String get apiValue {
    switch (this) {
      case PaymentMode.cash:
        return 'Cash';
      case PaymentMode.upi:
        return 'UPI';
      case PaymentMode.card:
        return 'Card';
      case PaymentMode.bankTransfer:
        return 'Bank Transfer';
      case PaymentMode.mixed:
        return 'Mixed';
    }
  }

  String label(AppLocalizations l10n) {
    switch (this) {
      case PaymentMode.cash:
        return l10n.paymentModeCash;
      case PaymentMode.upi:
        return l10n.paymentModeUpi;
      case PaymentMode.card:
        return l10n.paymentModeCard;
      case PaymentMode.bankTransfer:
        return l10n.paymentModeBankTransfer;
      case PaymentMode.mixed:
        return l10n.paymentModeMixed;
    }
  }
}
