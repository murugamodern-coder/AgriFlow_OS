import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/service_visit_model.dart';
import '../providers/service_provider.dart';

/// Visit detail screen with checklist and completion form.
class VisitDetailScreen extends ConsumerStatefulWidget {
  const VisitDetailScreen({super.key, required this.visit});

  final ServiceVisit visit;

  @override
  ConsumerState<VisitDetailScreen> createState() => _VisitDetailScreenState();
}

class _VisitDetailScreenState extends ConsumerState<VisitDetailScreen> {
  late bool _dripPipesIntact;
  late bool _drippersClogged;
  late bool _filterClean;
  late bool _valveWorking;
  late bool _pumpMotorOk;

  late final TextEditingController _issuesController;
  late final TextEditingController _actionsController;
  late double _satisfaction;
  late bool _followUp;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _dripPipesIntact = widget.visit.dripPipesIntact;
    _drippersClogged = widget.visit.drippersClogged;
    _filterClean = widget.visit.filterClean;
    _valveWorking = widget.visit.valveWorking;
    _pumpMotorOk = widget.visit.pumpMotorOk;
    _issuesController = TextEditingController(text: widget.visit.issuesFound ?? '');
    _actionsController = TextEditingController(text: widget.visit.actionsTaken ?? '');
    _satisfaction = widget.visit.farmerSatisfaction ?? 4.0;
    _followUp = widget.visit.followUpRequired;
  }

  @override
  void dispose() {
    _issuesController.dispose();
    _actionsController.dispose();
    super.dispose();
  }

  Future<void> _completeVisit() async {
    setState(() => _saving = true);
    try {
      final api = ref.read(serviceApiProvider);
      await api.completeVisit(
        visitName: widget.visit.name,
        dripPipesIntact: _dripPipesIntact,
        drippersClogged: _drippersClogged,
        filterClean: _filterClean,
        valveWorking: _valveWorking,
        pumpMotorOk: _pumpMotorOk,
        issuesFound: _issuesController.text,
        actionsTaken: _actionsController.text,
        farmerSatisfaction: _satisfaction,
        followUpRequired: _followUp,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Visit completed / பார்வை முடிந்தது'),
            backgroundColor: Colors.green,
          ),
        );
        ref.invalidate(upcomingVisitsProvider);
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isCompleted = widget.visit.completed;

    return Scaffold(
      appBar: AppBar(
        title: Text('Visit ${widget.visit.visitNumber} of 6'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // -- Header info --
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Visit: ${widget.visit.name}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text('Farmer / விவசாயி: ${widget.visit.farmer}'),
                    Text('Project / திட்டம்: ${widget.visit.farmerProject}'),
                    Text(
                      'Scheduled / திட்டமிட்ட: ${widget.visit.scheduledDate ?? "-"}',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // -- Checklist --
            const Text(
              'Service Checklist / பணி பட்டியல்',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Card(
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text(
                      'Drip Pipes Intact / குழாய்கள் சரியா',
                    ),
                    value: _dripPipesIntact,
                    onChanged: isCompleted
                        ? null
                        : (v) => setState(() => _dripPipesIntact = v),
                  ),
                  SwitchListTile(
                    title: const Text(
                      'Drippers Clogged / டிரிப்பர் அடைப்பு',
                    ),
                    value: _drippersClogged,
                    onChanged: isCompleted
                        ? null
                        : (v) => setState(() => _drippersClogged = v),
                  ),
                  SwitchListTile(
                    title: const Text(
                      'Filter Clean / வடிகட்டி சுத்தம்',
                    ),
                    value: _filterClean,
                    onChanged: isCompleted
                        ? null
                        : (v) => setState(() => _filterClean = v),
                  ),
                  SwitchListTile(
                    title: const Text(
                      'Valve Working / வால்வு வேலை',
                    ),
                    value: _valveWorking,
                    onChanged: isCompleted
                        ? null
                        : (v) => setState(() => _valveWorking = v),
                  ),
                  SwitchListTile(
                    title: const Text(
                      'Pump/Motor OK / பம்ப் சரியா',
                    ),
                    value: _pumpMotorOk,
                    onChanged: isCompleted
                        ? null
                        : (v) => setState(() => _pumpMotorOk = v),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // -- Notes --
            const Text(
              'Notes / குறிப்புகள்',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _issuesController,
              enabled: !isCompleted,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Issues Found / பிரச்சினைகள்',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _actionsController,
              enabled: !isCompleted,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Actions Taken / எடுக்கப்பட்ட நடவடிக்கைகள்',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),

            // -- Satisfaction --
            const Text(
              'Farmer Satisfaction / விவசாயி திருப்தி',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Slider(
              value: _satisfaction,
              min: 1,
              max: 5,
              divisions: 4,
              label: _satisfaction.toStringAsFixed(1),
              onChanged:
                  isCompleted ? null : (v) => setState(() => _satisfaction = v),
            ),
            const SizedBox(height: 16),

            // -- Follow-up --
            SwitchListTile(
              title: const Text(
                'Follow-up Required / மறுபடி பார்க்க வேண்டும்',
              ),
              value: _followUp,
              onChanged:
                  isCompleted ? null : (v) => setState(() => _followUp = v),
            ),
            const SizedBox(height: 24),

            // -- Complete button --
            if (!isCompleted)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _saving ? null : _completeVisit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade700,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  icon: _saving
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : const Icon(Icons.check_circle),
                  label: Text(
                    _saving ? 'Saving...' : 'Mark Complete / முடித்தது',
                  ),
                ),
              )
            else
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade300),
                ),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green.shade700),
                    const SizedBox(width: 8),
                    const Text(
                      'Visit Completed / பார்வை முடிந்தது',
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}