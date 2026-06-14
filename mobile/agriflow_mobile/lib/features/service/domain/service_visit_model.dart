/// Domain model for a Service Visit (M7 AMC).
///
/// Maps to Frappe DocType "Service Visit" fields.
class ServiceVisit {
  const ServiceVisit({
    required this.name,
    required this.farmerProject,
    required this.farmer,
    required this.visitNumber,
    this.scheduledDate,
    this.actualVisitDate,
    this.technician,
    this.visitStatus = 'Scheduled',
    this.completed = false,
    this.dripPipesIntact = false,
    this.drippersClogged = false,
    this.filterClean = false,
    this.valveWorking = false,
    this.pumpMotorOk = false,
    this.issuesFound,
    this.actionsTaken,
    this.farmerSatisfaction,
    this.followUpRequired = false,
    this.followUpDate,
  });

  final String name;
  final String farmerProject;
  final String farmer;
  final int visitNumber;
  final String? scheduledDate;
  final String? actualVisitDate;
  final String? technician;
  final String visitStatus;
  final bool completed;

  // Checklist fields
  final bool dripPipesIntact;
  final bool drippersClogged;
  final bool filterClean;
  final bool valveWorking;
  final bool pumpMotorOk;

  // Notes
  final String? issuesFound;
  final String? actionsTaken;
  final double? farmerSatisfaction;

  // Follow-up
  final bool followUpRequired;
  final String? followUpDate;

  /// Parse from Frappe API JSON.
  factory ServiceVisit.fromJson(Map<String, dynamic> json) {
    return ServiceVisit(
      name: json['name'] as String? ?? '',
      farmerProject: json['farmer_project'] as String? ?? '',
      farmer: json['farmer'] as String? ?? '',
      visitNumber: (json['visit_number'] is int)
          ? json['visit_number'] as int
          : int.tryParse('${json['visit_number']}') ?? 1,
      scheduledDate: json['scheduled_date']?.toString(),
      actualVisitDate: json['actual_visit_date']?.toString(),
      technician: json['technician']?.toString(),
      visitStatus: json['visit_status'] as String? ?? 'Scheduled',
      completed: json['completed'] == 1 || json['completed'] == true,
      dripPipesIntact: json['drip_pipes_intact'] == 1,
      drippersClogged: json['drippers_clogged'] == 1,
      filterClean: json['filter_clean'] == 1,
      valveWorking: json['valve_working'] == 1,
      pumpMotorOk: json['pump_motor_ok'] == 1,
      issuesFound: json['issues_found']?.toString(),
      actionsTaken: json['actions_taken']?.toString(),
      farmerSatisfaction: (json['farmer_satisfaction'] is num)
          ? (json['farmer_satisfaction'] as num).toDouble()
          : null,
      followUpRequired: json['follow_up_required'] == 1,
      followUpDate: json['follow_up_date']?.toString(),
    );
  }
}