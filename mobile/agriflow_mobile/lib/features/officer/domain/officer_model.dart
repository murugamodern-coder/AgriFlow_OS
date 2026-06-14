/// Domain model for a Government Officer (M8).
class GovernmentOfficer {
  const GovernmentOfficer({
    required this.name,
    required this.officerName,
    required this.designation,
    required this.mobile,
    this.email,
    this.officeLocation,
    this.district,
    this.block,
    this.activeProjects = 0,
  });

  final String name;
  final String officerName;
  final String designation;
  final String mobile;
  final String? email;
  final String? officeLocation;
  final String? district;
  final String? block;
  final int activeProjects;

  factory GovernmentOfficer.fromJson(Map<String, dynamic> json) {
    return GovernmentOfficer(
      name: json['name'] as String? ?? json['officer_id'] as String? ?? '',
      officerName: json['officer_name'] as String? ?? '',
      designation: json['designation'] as String? ?? '',
      mobile: json['mobile'] as String? ?? '',
      email: json['email']?.toString(),
      officeLocation: json['office_location']?.toString(),
      district: json['district']?.toString(),
      block: json['block']?.toString(),
      activeProjects: (json['active_projects'] is int)
          ? json['active_projects'] as int
          : int.tryParse('${json['active_projects'] ?? 0}') ?? 0,
    );
  }
}