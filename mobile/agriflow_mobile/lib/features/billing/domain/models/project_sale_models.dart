import 'package:agriflow_mobile/features/billing/domain/models/billing_models.dart';

/// Quotation cart for a linked Farmer Project (Project Sale billing mode).
class ProjectSaleQuote {
  const ProjectSaleQuote({
    required this.projectName,
    required this.farmerName,
    required this.items,
    this.subsidyAmount = 0,
    this.farmerPortion = 0,
    this.paymentMode = PaymentMode.cash,
  });

  final String projectName;
  final String farmerName;
  final List<CartLine> items;
  final double subsidyAmount;
  final double farmerPortion;
  final PaymentMode paymentMode;

  double get totalAmount =>
      items.fold(0.0, (sum, line) => sum + line.amount);

  /// Tamil Nadu drip subsidy default: 80% govt / 20% farmer.
  double get autoSubsidyAmount => totalAmount * 0.80;

  double get autoFarmerPortion => totalAmount - autoSubsidyAmount;

  bool get isValid =>
      items.isNotEmpty &&
      (subsidyAmount + farmerPortion).round() == totalAmount.round();

  ProjectSaleQuote copyWith({
    String? projectName,
    String? farmerName,
    List<CartLine>? items,
    double? subsidyAmount,
    double? farmerPortion,
    PaymentMode? paymentMode,
  }) {
    return ProjectSaleQuote(
      projectName: projectName ?? this.projectName,
      farmerName: farmerName ?? this.farmerName,
      items: items ?? this.items,
      subsidyAmount: subsidyAmount ?? this.subsidyAmount,
      farmerPortion: farmerPortion ?? this.farmerPortion,
      paymentMode: paymentMode ?? this.paymentMode,
    );
  }

  ProjectSaleQuote withAutoSplit() {
    return copyWith(
      subsidyAmount: autoSubsidyAmount,
      farmerPortion: autoFarmerPortion,
    );
  }
}
