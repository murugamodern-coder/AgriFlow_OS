import 'package:flutter/material.dart';

class DashboardKpiCard extends StatelessWidget {
  const DashboardKpiCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  final String label;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class DashboardActionTile extends StatelessWidget {
  const DashboardActionTile({
    super.key,
    required this.label,
    required this.icon,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 28, color: Theme.of(context).colorScheme.primary),
              const SizedBox(height: 8),
              Text(
                label,
                style: Theme.of(context).textTheme.labelMedium,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class DashboardBigButton extends StatelessWidget {
  const DashboardBigButton({
    super.key,
    required this.label,
    required this.icon,
    required this.onTap,
    this.color,
  });

  final String label;
  final IconData icon;
  final VoidCallback onTap;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
          backgroundColor: color,
          foregroundColor: color != null ? Colors.white : null,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 32),
            const SizedBox(height: 8),
            Text(label, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

class DashboardSectionTitle extends StatelessWidget {
  const DashboardSectionTitle({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }
}

class DashboardStatsRow extends StatelessWidget {
  const DashboardStatsRow({
    super.key,
    required this.projectCount,
    required this.openTaskCount,
    required this.projectsLabel,
    required this.tasksLabel,
  });

  final int projectCount;
  final int openTaskCount;
  final String projectsLabel;
  final String tasksLabel;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final narrow = constraints.maxWidth < 480;
        final cards = [
          Expanded(
            child: DashboardKpiCard(
              label: projectsLabel,
              value: '$projectCount',
              icon: Icons.account_tree_outlined,
              color: Colors.orange,
            ),
          ),
          Expanded(
            child: DashboardKpiCard(
              label: tasksLabel,
              value: '$openTaskCount',
              icon: Icons.task_alt,
              color: Colors.red,
            ),
          ),
        ];
        if (narrow) {
          return Column(
            children: [
              Row(children: cards),
            ],
          );
        }
        return Row(children: cards);
      },
    );
  }
}

int dashboardActionCrossAxisCount(BuildContext context) {
  final width = MediaQuery.sizeOf(context).width;
  if (width < 400) return 2;
  if (width < 700) return 3;
  return 4;
}
