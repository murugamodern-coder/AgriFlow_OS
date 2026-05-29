import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/pilot_ops/data/pilot_ops_remote.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class FeedbackScreen extends ConsumerStatefulWidget {
  const FeedbackScreen({super.key});

  @override
  ConsumerState<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends ConsumerState<FeedbackScreen> {
  final _body = TextEditingController();
  String _category = 'ux';
  String _severity = 'medium';
  bool _sending = false;

  @override
  void dispose() {
    _body.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final l10n = AppLocalizations.of(context)!;
    if (_body.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.feedbackBodyRequired)),
      );
      return;
    }
    setState(() => _sending = true);
    try {
      final deviceId = await ref.read(pilotTelemetryProvider).deviceId();
      await ref.read(pilotOpsRemoteProvider).submitFeedback({
        'device_id': deviceId,
        'app_version': Env.appVersion,
        'category': _category,
        'severity': _severity,
        'body': _body.text.trim(),
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.feedbackSent)),
        );
        Navigator.of(context).pop();
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.errorGeneric)),
        );
      }
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.feedbackTitle)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(l10n.feedbackHint, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _category,
            decoration: InputDecoration(labelText: l10n.feedbackCategory),
            items: [
              DropdownMenuItem(value: 'sync', child: Text(l10n.feedbackCatSync)),
              DropdownMenuItem(value: 'ux', child: Text(l10n.feedbackCatUx)),
              DropdownMenuItem(value: 'inventory', child: Text(l10n.feedbackCatInventory)),
              DropdownMenuItem(value: 'task', child: Text(l10n.feedbackCatTask)),
              DropdownMenuItem(value: 'network', child: Text(l10n.feedbackCatNetwork)),
              DropdownMenuItem(value: 'other', child: Text(l10n.feedbackCatOther)),
            ],
            onChanged: (v) => setState(() => _category = v ?? 'other'),
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: _severity,
            decoration: InputDecoration(labelText: l10n.feedbackSeverity),
            items: [
              DropdownMenuItem(value: 'low', child: Text(l10n.feedbackSevLow)),
              DropdownMenuItem(value: 'medium', child: Text(l10n.feedbackSevMedium)),
              DropdownMenuItem(value: 'high', child: Text(l10n.feedbackSevHigh)),
            ],
            onChanged: (v) => setState(() => _severity = v ?? 'medium'),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _body,
            maxLines: 6,
            decoration: InputDecoration(
              labelText: l10n.feedbackBodyLabel,
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: _sending ? null : _submit,
            child: _sending
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(l10n.feedbackSubmit),
          ),
        ],
      ),
    );
  }
}
