import 'package:equatable/equatable.dart';

class FarmerSummary extends Equatable {
  const FarmerSummary({
    required this.name,
    required this.farmerName,
    this.mobile,
    this.block,
    this.village,
  });

  final String name;
  final String farmerName;
  final String? mobile;
  final String? block;
  final String? village;

  factory FarmerSummary.fromJson(Map<String, dynamic> json) {
    return FarmerSummary(
      name: json['name'] as String? ?? '',
      farmerName: json['farmer_name'] as String? ?? '',
      mobile: json['mobile'] as String?,
      block: json['block'] as String?,
      village: json['village'] as String?,
    );
  }

  @override
  List<Object?> get props => [name, farmerName];
}
