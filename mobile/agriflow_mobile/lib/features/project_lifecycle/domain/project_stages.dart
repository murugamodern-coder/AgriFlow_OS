/// Canonical 12-stage subsidy workflow (matches backend fixtures).
abstract final class ProjectStages {
  static const ordered = [
    'lead_captured',
    'eligibility_check',
    'documents_collected',
    'mimis_registered',
    'field_survey',
    'quotation_generated',
    'pre_inspection_approval',
    'work_order_received',
    'material_dispatched',
    'installation_done',
    'post_inspection_approval',
    'subsidy_released',
  ];

  static int indexOf(String stageKey) {
    final i = ordered.indexOf(stageKey);
    return i < 0 ? 0 : i;
  }
}
