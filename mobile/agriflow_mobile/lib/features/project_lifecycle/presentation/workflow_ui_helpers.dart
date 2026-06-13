import 'package:agriflow_mobile/features/project_lifecycle/domain/models/workflow_state.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';

Color workflowColorFromName(String colorName, {bool muted = false}) {
  final color = switch (colorName) {
    'blue' => Colors.blue,
    'orange' => Colors.orange,
    'yellow' => Colors.amber,
    'green' => Colors.green,
    'purple' => Colors.deepPurple,
    _ => Colors.blueGrey,
  };
  return muted ? color.withValues(alpha: 0.35) : color;
}

String workflowStageLabel(AppLocalizations l10n, String stageKey) {
  switch (stageKey) {
    case 'lead_captured':
      return l10n.stageLeadCaptured;
    case 'eligibility_check':
      return l10n.stageEligibilityCheck;
    case 'documents_collected':
      return l10n.stageDocumentsCollected;
    case 'mimis_registered':
      return l10n.stageMimisRegistered;
    case 'field_survey':
      return l10n.stageFieldSurvey;
    case 'quotation_generated':
      return l10n.stageQuotationGenerated;
    case 'pre_inspection_approval':
      return l10n.stagePreInspectionApproval;
    case 'work_order_received':
      return l10n.stageWorkOrderReceived;
    case 'material_dispatched':
      return l10n.stageMaterialDispatched;
    case 'installation_done':
      return l10n.stageInstallationDone;
    case 'post_inspection_approval':
      return l10n.stagePostInspectionApproval;
    case 'subsidy_released':
      return l10n.stageSubsidyReleased;
    default:
      return stageKey.replaceAll('_', ' ');
  }
}

String workflowActionLabel(AppLocalizations l10n, String action) {
  switch (action) {
    case 'Verify Eligibility':
      return l10n.actionVerifyEligibility;
    case 'Collect Documents':
      return l10n.actionCollectDocuments;
    case 'Register in MIMIS':
      return l10n.actionRegisterInMimis;
    case 'Schedule Field Survey':
      return l10n.actionScheduleFieldSurvey;
    case 'Generate Quotation':
      return l10n.actionGenerateQuotation;
    case 'Submit for Pre-Inspection':
      return l10n.actionSubmitForPreInspection;
    case 'Receive Work Order':
      return l10n.actionReceiveWorkOrder;
    case 'Dispatch Material':
      return l10n.actionDispatchMaterial;
    case 'Complete Installation':
      return l10n.actionCompleteInstallation;
    case 'Submit for Post-Inspection':
      return l10n.actionSubmitForPostInspection;
    case 'Release Subsidy':
      return l10n.actionReleaseSubsidy;
    default:
      return action;
  }
}

String workflowNextStateLabel(AppLocalizations l10n, WorkflowAction action) {
  final normalized = action.nextState.toLowerCase();
  final key = switch (normalized) {
    'lead captured' => 'lead_captured',
    'eligibility check' => 'eligibility_check',
    'documents collected' => 'documents_collected',
    'mimis registered' => 'mimis_registered',
    'field survey' => 'field_survey',
    'quotation generated' => 'quotation_generated',
    'pre-inspection approval' => 'pre_inspection_approval',
    'work order received' => 'work_order_received',
    'material dispatched' => 'material_dispatched',
    'installation done' => 'installation_done',
    'post-inspection approval' => 'post_inspection_approval',
    'subsidy released' => 'subsidy_released',
    _ => normalized.replaceAll(' ', '_').replaceAll('-', '_'),
  };
  return workflowStageLabel(l10n, key);
}
