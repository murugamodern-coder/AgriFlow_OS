// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'AgriFlow OS';

  @override
  String get loginTitle => 'Sign in';

  @override
  String get loginUsername => 'Username';

  @override
  String get loginPassword => 'Password';

  @override
  String get loginSubmit => 'Continue';

  @override
  String get loginDevStub => 'Use dev session (debug only)';

  @override
  String get navTimeline => 'Timeline';

  @override
  String get navTasks => 'My Tasks';

  @override
  String get navNotifications => 'Notifications';

  @override
  String get navSync => 'Sync';

  @override
  String get syncStatusTitle => 'Sync status';

  @override
  String get syncNow => 'Sync now';

  @override
  String syncPending(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count pending changes',
      one: '1 pending change',
      zero: 'No pending changes',
    );
    return '$_temp0';
  }

  @override
  String get syncInProgress => 'Syncing…';

  @override
  String syncLastSuccess(String time) {
    return 'Last sync: $time';
  }

  @override
  String get offlineBanner =>
      'You are offline — changes will sync when connected';

  @override
  String get degradedNetworkBanner =>
      'Slow or limited connection — sync may take longer';

  @override
  String offlinePendingHint(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count changes waiting to sync',
      one: '1 change waiting to sync',
    );
    return '$_temp0';
  }

  @override
  String syncPhaseLabel(String phase) {
    return 'Sync step: $phase';
  }

  @override
  String queueRepairResult(int reset, int deduped) {
    return 'Queue repair: $reset reset, $deduped duplicates removed';
  }

  @override
  String get conflictStepsTitle => 'What to do';

  @override
  String get conflictStepRefresh =>
      'Tap Refresh to pull the latest server data';

  @override
  String get conflictStepReview => 'Review your task or inventory change';

  @override
  String get conflictStepRetry => 'Make the change again if still needed';

  @override
  String get emptyTasks => 'No tasks in your inbox';

  @override
  String get emptyTimeline => 'No timeline events yet';

  @override
  String get emptyNotifications => 'No notifications';

  @override
  String get errorGeneric => 'Something went wrong';

  @override
  String get retry => 'Retry';

  @override
  String get taskComplete => 'Mark complete';

  @override
  String get conflictTitle => 'Sync conflict';

  @override
  String get conflictExplanation =>
      'The server has a newer version of this record. Your offline change cannot apply until you refresh and try again.';

  @override
  String get conflictRefresh => 'Refresh from server';

  @override
  String deviceHealthLabel(String score) {
    return 'Device health: $score';
  }

  @override
  String get deviceStaleWarning =>
      'Device not synced recently — open app on Wi‑Fi';

  @override
  String get notificationMarkRead => 'Mark read';

  @override
  String get logout => 'Sign out';

  @override
  String get feedbackTitle => 'Pilot feedback';

  @override
  String get feedbackHint =>
      'Describe what happened in the field. No farmer PII in free text.';

  @override
  String get feedbackCategory => 'Category';

  @override
  String get feedbackSeverity => 'Severity';

  @override
  String get feedbackBodyLabel => 'Details';

  @override
  String get feedbackBodyRequired => 'Please enter feedback details';

  @override
  String get feedbackSubmit => 'Send feedback';

  @override
  String get feedbackSent => 'Feedback sent — thank you';

  @override
  String get feedbackCatSync => 'Sync';

  @override
  String get feedbackCatUx => 'App UX';

  @override
  String get feedbackCatInventory => 'Inventory';

  @override
  String get feedbackCatTask => 'Tasks';

  @override
  String get feedbackCatNetwork => 'Network';

  @override
  String get feedbackCatOther => 'Other';

  @override
  String get feedbackSevLow => 'Low';

  @override
  String get feedbackSevMedium => 'Medium';

  @override
  String get feedbackSevHigh => 'High';

  @override
  String get onboardingTitle => 'Field onboarding';

  @override
  String get onboardingIntro =>
      'Complete these steps before your first pilot day.';

  @override
  String get onboardingLogin => 'Sign in with your officer account';

  @override
  String get onboardingInitialSync => 'Run a full sync on Wi‑Fi';

  @override
  String get onboardingReviewTasks => 'Open My Tasks and review assignments';

  @override
  String get onboardingOfflineTest =>
      'Optional: turn off data and confirm cached views';

  @override
  String get onboardingFeedback =>
      'Know how to send pilot feedback from the menu';

  @override
  String get onboardingRequired => 'Recommended';

  @override
  String get onboardingDone => 'Continue to app';

  @override
  String appVersionLabel(String version) {
    return 'App version $version';
  }

  @override
  String get navHome => 'Home';

  @override
  String get navFarmers => 'Farmers';

  @override
  String dashboardWelcome(String name) {
    return 'Welcome, $name';
  }

  @override
  String dashboardRoleLine(String role) {
    return 'Role: $role';
  }

  @override
  String dashboardBlocksLine(String blocks) {
    return 'Blocks: $blocks';
  }

  @override
  String get dashboardProjects => 'Projects';

  @override
  String get dashboardOpenTasks => 'Open tasks';

  @override
  String get dashboardViewFarmers => 'View farmers';

  @override
  String get roleOwner => 'Owner';

  @override
  String get roleOfficeManager => 'Office Manager';

  @override
  String get roleFieldStaff => 'Field Staff';

  @override
  String get roleUser => 'User';

  @override
  String get emptyFarmers => 'No farmers found';

  @override
  String get noProjectForFarmer => 'No active project for this farmer';

  @override
  String get projectTimelineTitle => 'Project timeline';

  @override
  String advanceStage(String stage) {
    return 'Advance to $stage';
  }

  @override
  String get stageTransitionSuccess => 'Stage updated — sync to refresh tasks';

  @override
  String get timelineNoteLabel => 'Note';

  @override
  String get timelineNoteQueue => 'Queue note';

  @override
  String get syncLastRequestId => 'Last request ID';

  @override
  String get syncRepairQueue => 'Repair queue';

  @override
  String get taskMaterialsTitle => 'Materials';

  @override
  String get taskConsumeOne => 'Consume 1';

  @override
  String get notificationTaskDue => 'Task due';

  @override
  String get notificationTaskOverdue => 'Task overdue';

  @override
  String get notificationStageTransition => 'Stage updated';

  @override
  String get notificationProjectStatus => 'Project update';

  @override
  String get notificationSlaBreach => 'SLA breach';

  @override
  String get notificationManual => 'Notification';

  @override
  String get stageLeadCaptured => 'Lead captured';

  @override
  String get stageEligibilityCheck => 'Eligibility check';

  @override
  String get stageDocumentsCollected => 'Documents collected';

  @override
  String get stageMimisRegistered => 'MIMIS registered';

  @override
  String get stageFieldSurvey => 'Field survey';

  @override
  String get stageQuotationGenerated => 'Quotation generated';

  @override
  String get stagePreInspectionApproval => 'Pre-inspection approval';

  @override
  String get stageWorkOrderReceived => 'Work order received';

  @override
  String get stageMaterialDispatched => 'Material dispatched';

  @override
  String get stageInstallationDone => 'Installation done';

  @override
  String get stagePostInspectionApproval => 'Post-inspection approval';

  @override
  String get stageSubsidyReleased => 'Subsidy released';

  @override
  String get timelineStageToday => 'TODAY';

  @override
  String get timelineStagePending => 'Pending';

  @override
  String get timelineStageLocked => 'Locked';

  @override
  String timelineStageBy(String name) {
    return 'By $name';
  }

  @override
  String get timelineActionCall => 'Call';

  @override
  String get timelineActionWhatsapp => 'WhatsApp';

  @override
  String get timelineActionNote => 'Note';

  @override
  String timelineBlockerMissing(String item) {
    return 'Missing: $item';
  }

  @override
  String timelineHeaderLocation(String block, String village, String acres) {
    return '$block · $village$acres';
  }

  @override
  String get timelineHeaderSchemeDrip => 'Drip irrigation · subsidy project';

  @override
  String get timelineHeaderSchemeSubsidy => 'Subsidy drip project';

  @override
  String timelineHeaderProject(String id) {
    return 'Project $id';
  }

  @override
  String timelineHeaderOfficer(String name) {
    return 'Officer: $name';
  }

  @override
  String timelineHeaderReferral(String name) {
    return 'Referred by: $name';
  }

  @override
  String get timelineAcres => 'acres';

  @override
  String get taskFeedTitle => 'Today\'s work';

  @override
  String taskFeedSummary(int pending, int overdue) {
    return '$pending pending · $overdue overdue';
  }

  @override
  String get taskSectionOverdue => 'Overdue';

  @override
  String get taskSectionToday => 'Today';

  @override
  String get taskSectionUpcoming => 'Upcoming';

  @override
  String get taskFeedEmptyCelebration => '🎉 No pending tasks today!';

  @override
  String get taskFilterAll => 'All';

  @override
  String get taskFilterMine => 'My tasks';

  @override
  String get taskFilterVisit => 'Visit';

  @override
  String get taskFilterDocument => 'Documents';

  @override
  String get taskDueToday => 'Due today';

  @override
  String taskDueDaysAgo(int days) {
    return '$days days ago';
  }

  @override
  String taskDueInDays(int days) {
    return 'In $days days';
  }

  @override
  String get taskGpsCheckIn => 'GPS check-in at field';

  @override
  String get taskGpsCheckedIn => 'Checked in at field';

  @override
  String get taskVoiceNoteAttach => 'Attach voice note';

  @override
  String get taskVoiceNoteQueued => 'Voice note queued for sync';

  @override
  String get notificationMarkAllRead => 'Mark all read';

  @override
  String get notificationEmptyFriendly =>
      'You\'re all caught up — no new alerts.';

  @override
  String get notificationFilterAll => 'All';

  @override
  String get notificationFilterUrgent => 'Urgent';

  @override
  String get notificationFilterTasks => 'Tasks';

  @override
  String get notificationGroupToday => 'Today';

  @override
  String get notificationGroupYesterday => 'Yesterday';

  @override
  String get notificationGroupThisWeek => 'This week';

  @override
  String get notificationGroupOlder => 'Older';

  @override
  String get notificationFollowupMissed => 'Missed follow-up';

  @override
  String get notificationStageStuck => 'Stage stuck';

  @override
  String get notificationOfficerTransfer => 'Officer transfer';

  @override
  String get notificationLowStock => 'Low stock alert';

  @override
  String get notificationTaskCompleted => 'Task completed';

  @override
  String syncBarOnline(int count) {
    return 'Online · $count pending';
  }

  @override
  String syncBarOffline(int count) {
    return 'Offline · $count pending';
  }

  @override
  String syncBarSyncing(int current, int total) {
    return 'Syncing $current of $total…';
  }

  @override
  String get syncBarJustSynced => 'All synced just now';

  @override
  String get syncBarTapHintOnline => 'Tap Sync tab to force refresh';

  @override
  String get syncBarTapHintOffline =>
      'Changes saved locally — sync when online';

  @override
  String get syncToastSavedOffline => 'Saved offline ✓';

  @override
  String get syncToastComplete => 'Synced ✓';

  @override
  String get syncToastStarted => 'Syncing your changes…';

  @override
  String get syncForceNow => 'Force sync now';

  @override
  String syncLastSuccessLabel(String time) {
    return 'Last successful sync: $time';
  }

  @override
  String syncPendingChanges(int count) {
    return 'Pending changes: $count items';
  }

  @override
  String get syncPendingListTitle => 'Pending queue';

  @override
  String get syncPendingListEmpty => 'No pending changes in queue';

  @override
  String get syncHistoryTitle => 'Sync history (last 10)';

  @override
  String get syncHistoryEmpty => 'No sync runs logged yet';

  @override
  String get syncHistoryOk => 'OK';

  @override
  String get syncHistoryFail => 'Failed';

  @override
  String get syncDeveloperTitle => 'Developer (demo)';

  @override
  String get syncSimulateOffline => 'Simulate offline';

  @override
  String get syncSimulateOfflineHint =>
      'Queue writes without network — for live demo';

  @override
  String get syncSimulateOfflineOn => 'Simulated offline ON';

  @override
  String get syncSimulateOfflineOff => 'Simulated offline OFF';

  @override
  String get syncDemoFlowButton => 'Demo: go online & sync';

  @override
  String get syncNever => 'Never';

  @override
  String get syncJustNow => 'Just now';

  @override
  String syncMinutesAgo(int minutes) {
    return '$minutes min ago';
  }

  @override
  String syncHoursAgo(int hours) {
    return '$hours hr ago';
  }

  @override
  String sectionWithCount(String label, int count) {
    return '$label ($count)';
  }

  @override
  String syncFlyingItem(int index) {
    return 'Upload $index';
  }

  @override
  String conflictStepNumbered(int step, String text) {
    return '$step. $text';
  }

  @override
  String conflictMutationId(String id) {
    return 'Mutation: $id';
  }

  @override
  String conflictVersionLine(int server, int client) {
    return 'Server v$server · Client v$client';
  }

  @override
  String get conflictCodeDefault => 'Sync conflict';

  @override
  String syncQueueItemTitle(String entity, String op) {
    return '$entity · $op';
  }

  @override
  String taskFarmerVillageLine(String farmer, String village) {
    return '$farmer · $village';
  }

  @override
  String taskStatusProjectLine(String status, String project) {
    return '$status · $project';
  }

  @override
  String taskReservedQty(String qty, String status) {
    return 'Reserved $qty · $status';
  }

  @override
  String updateRequiredMessage(String version) {
    return 'Update required (minimum $version)';
  }

  @override
  String get stageSecondaryDocsComplete => '4/4 documents uploaded';

  @override
  String stageSecondaryMimisId(String id) {
    return 'ID: $id';
  }

  @override
  String stageSecondaryQuotation(String amount) {
    return '₹$amount';
  }

  @override
  String get stageSecondaryAaoApproved => 'AAO approved';

  @override
  String get stageSecondaryStockReserved => 'Stock reserved';

  @override
  String get stageSecondaryInstallationTeam => 'Murugan installation team';
}
