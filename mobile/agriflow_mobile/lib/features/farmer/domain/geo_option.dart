class GeoOption {
  const GeoOption({
    required this.name,
    required this.label,
    this.lgdCode,
    this.pincode,
  });

  final String name;
  final String label;
  final String? lgdCode;
  final String? pincode;

  factory GeoOption.fromJson(Map<String, dynamic> json, {required String labelKey}) {
    return GeoOption(
      name: json['name'] as String? ?? '',
      label: json[labelKey] as String? ?? json['name'] as String? ?? '',
      lgdCode: json['lgd_code'] as String?,
      pincode: json['pincode'] as String?,
    );
  }
}
