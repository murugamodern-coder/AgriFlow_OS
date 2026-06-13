import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/models/workflow_state.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/providers/workflow_provider.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// Shown on project timeline when workflow is at Quotation Generated.
class TimelineProjectSaleButton extends ConsumerWidget {
  const TimelineProjectSaleButton({
    super.key,
    required this.projectName,
    this.farmerDisplayName,
  });

  final String projectName;
  final String? farmerDisplayName;

  static bool isQuotationStage(WorkflowStatus workflow) {
    return workflow.currentState == 'Quotation Generated' ||
        workflow.currentStage == 'quotation_generated';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workflowAsync = ref.watch(projectWorkflowProvider(projectName));
    final l10n = AppLocalizations.of(context)!;

    return workflowAsync.when(
      data: (workflow) {
        if (!isQuotationStage(workflow)) {
          return const SizedBox.shrink();
        }
        return Padding(
          padding: const EdgeInsets.only(bottom: AgriFlowSpacing.space8),
          child: ElevatedButton.icon(
            icon: const Icon(Icons.receipt_long),
            label: Text(l10n.generateProjectInvoice),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.amber.shade800,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              minimumSize: const Size(double.infinity, 0),
            ),
            onPressed: () => context.push(AppRoutes.projectSale(projectName)),
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}
