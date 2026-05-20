import 'package:flutter/widgets.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

/// Resolves server i18n keys and stage keys for Tamil-first demo UI.
abstract final class AgriFlowI18n {
  static String stageLabel(BuildContext context, String stageKey) {
    final l10n = AppLocalizations.of(context)!;
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

  static String notificationTitle(BuildContext context, String key) {
    final l10n = AppLocalizations.of(context)!;
    switch (key) {
      case 'notification.task_due':
        return l10n.notificationTaskDue;
      case 'notification.task_overdue':
        return l10n.notificationTaskOverdue;
      case 'notification.stage_transition':
        return l10n.notificationStageTransition;
      case 'notification.project_status':
        return l10n.notificationProjectStatus;
      case 'notification.sla_breach':
        return l10n.notificationSlaBreach;
      case 'notification.manual':
        return l10n.notificationManual;
      case 'notificationFollowupMissed':
        return l10n.notificationFollowupMissed;
      case 'notificationStageStuck':
        return l10n.notificationStageStuck;
      case 'notificationOfficerTransfer':
        return l10n.notificationOfficerTransfer;
      case 'notificationLowStock':
        return l10n.notificationLowStock;
      case 'notificationTaskCompleted':
        return l10n.notificationTaskCompleted;
      default:
        if (key.startsWith('notification.')) {
          return key.substring('notification.'.length).replaceAll('_', ' ');
        }
        return key;
    }
  }
}
