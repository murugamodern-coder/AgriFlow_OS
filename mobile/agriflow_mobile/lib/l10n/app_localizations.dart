import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_ta.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ta'),
    Locale('en')
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'AgriFlow OS'**
  String get appTitle;

  /// No description provided for @loginTitle.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get loginTitle;

  /// No description provided for @loginUsername.
  ///
  /// In en, this message translates to:
  /// **'Username'**
  String get loginUsername;

  /// No description provided for @loginPassword.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get loginPassword;

  /// No description provided for @loginSubmit.
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get loginSubmit;

  /// No description provided for @loginDevStub.
  ///
  /// In en, this message translates to:
  /// **'Use dev session (debug only)'**
  String get loginDevStub;

  /// No description provided for @navTimeline.
  ///
  /// In en, this message translates to:
  /// **'Timeline'**
  String get navTimeline;

  /// No description provided for @navTasks.
  ///
  /// In en, this message translates to:
  /// **'My Tasks'**
  String get navTasks;

  /// No description provided for @navNotifications.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get navNotifications;

  /// No description provided for @navSync.
  ///
  /// In en, this message translates to:
  /// **'Sync'**
  String get navSync;

  /// No description provided for @syncStatusTitle.
  ///
  /// In en, this message translates to:
  /// **'Sync status'**
  String get syncStatusTitle;

  /// No description provided for @syncNow.
  ///
  /// In en, this message translates to:
  /// **'Sync now'**
  String get syncNow;

  /// No description provided for @syncPending.
  ///
  /// In en, this message translates to:
  /// **'{count, plural, =0{No pending changes} one{1 pending change} other{{count} pending changes}}'**
  String syncPending(int count);

  /// No description provided for @syncInProgress.
  ///
  /// In en, this message translates to:
  /// **'Syncing…'**
  String get syncInProgress;

  /// No description provided for @syncLastSuccess.
  ///
  /// In en, this message translates to:
  /// **'Last sync: {time}'**
  String syncLastSuccess(String time);

  /// No description provided for @offlineBanner.
  ///
  /// In en, this message translates to:
  /// **'You are offline — changes will sync when connected'**
  String get offlineBanner;

  /// No description provided for @degradedNetworkBanner.
  ///
  /// In en, this message translates to:
  /// **'Slow or limited connection — sync may take longer'**
  String get degradedNetworkBanner;

  /// No description provided for @offlinePendingHint.
  ///
  /// In en, this message translates to:
  /// **'{count, plural, one{1 change waiting to sync} other{{count} changes waiting to sync}}'**
  String offlinePendingHint(int count);

  /// No description provided for @syncPhaseLabel.
  ///
  /// In en, this message translates to:
  /// **'Sync step: {phase}'**
  String syncPhaseLabel(String phase);

  /// No description provided for @queueRepairResult.
  ///
  /// In en, this message translates to:
  /// **'Queue repair: {reset} reset, {deduped} duplicates removed'**
  String queueRepairResult(int reset, int deduped);

  /// No description provided for @conflictStepsTitle.
  ///
  /// In en, this message translates to:
  /// **'What to do'**
  String get conflictStepsTitle;

  /// No description provided for @conflictStepRefresh.
  ///
  /// In en, this message translates to:
  /// **'Tap Refresh to pull the latest server data'**
  String get conflictStepRefresh;

  /// No description provided for @conflictStepReview.
  ///
  /// In en, this message translates to:
  /// **'Review your task or inventory change'**
  String get conflictStepReview;

  /// No description provided for @conflictStepRetry.
  ///
  /// In en, this message translates to:
  /// **'Make the change again if still needed'**
  String get conflictStepRetry;

  /// No description provided for @emptyTasks.
  ///
  /// In en, this message translates to:
  /// **'No tasks in your inbox'**
  String get emptyTasks;

  /// No description provided for @emptyTimeline.
  ///
  /// In en, this message translates to:
  /// **'No timeline events yet'**
  String get emptyTimeline;

  /// No description provided for @emptyNotifications.
  ///
  /// In en, this message translates to:
  /// **'No notifications'**
  String get emptyNotifications;

  /// No description provided for @errorGeneric.
  ///
  /// In en, this message translates to:
  /// **'Something went wrong'**
  String get errorGeneric;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @taskComplete.
  ///
  /// In en, this message translates to:
  /// **'Mark complete'**
  String get taskComplete;

  /// No description provided for @conflictTitle.
  ///
  /// In en, this message translates to:
  /// **'Sync conflict'**
  String get conflictTitle;

  /// No description provided for @conflictExplanation.
  ///
  /// In en, this message translates to:
  /// **'The server has a newer version of this record. Your offline change cannot apply until you refresh and try again.'**
  String get conflictExplanation;

  /// No description provided for @conflictRefresh.
  ///
  /// In en, this message translates to:
  /// **'Refresh from server'**
  String get conflictRefresh;

  /// No description provided for @deviceHealthLabel.
  ///
  /// In en, this message translates to:
  /// **'Device health: {score}'**
  String deviceHealthLabel(String score);

  /// No description provided for @deviceStaleWarning.
  ///
  /// In en, this message translates to:
  /// **'Device not synced recently — open app on Wi‑Fi'**
  String get deviceStaleWarning;

  /// No description provided for @notificationMarkRead.
  ///
  /// In en, this message translates to:
  /// **'Mark read'**
  String get notificationMarkRead;

  /// No description provided for @logout.
  ///
  /// In en, this message translates to:
  /// **'Sign out'**
  String get logout;

  /// No description provided for @feedbackTitle.
  ///
  /// In en, this message translates to:
  /// **'Pilot feedback'**
  String get feedbackTitle;

  /// No description provided for @feedbackHint.
  ///
  /// In en, this message translates to:
  /// **'Describe what happened in the field. No farmer PII in free text.'**
  String get feedbackHint;

  /// No description provided for @feedbackCategory.
  ///
  /// In en, this message translates to:
  /// **'Category'**
  String get feedbackCategory;

  /// No description provided for @feedbackSeverity.
  ///
  /// In en, this message translates to:
  /// **'Severity'**
  String get feedbackSeverity;

  /// No description provided for @feedbackBodyLabel.
  ///
  /// In en, this message translates to:
  /// **'Details'**
  String get feedbackBodyLabel;

  /// No description provided for @feedbackBodyRequired.
  ///
  /// In en, this message translates to:
  /// **'Please enter feedback details'**
  String get feedbackBodyRequired;

  /// No description provided for @feedbackSubmit.
  ///
  /// In en, this message translates to:
  /// **'Send feedback'**
  String get feedbackSubmit;

  /// No description provided for @feedbackSent.
  ///
  /// In en, this message translates to:
  /// **'Feedback sent — thank you'**
  String get feedbackSent;

  /// No description provided for @feedbackCatSync.
  ///
  /// In en, this message translates to:
  /// **'Sync'**
  String get feedbackCatSync;

  /// No description provided for @feedbackCatUx.
  ///
  /// In en, this message translates to:
  /// **'App UX'**
  String get feedbackCatUx;

  /// No description provided for @feedbackCatInventory.
  ///
  /// In en, this message translates to:
  /// **'Inventory'**
  String get feedbackCatInventory;

  /// No description provided for @feedbackCatTask.
  ///
  /// In en, this message translates to:
  /// **'Tasks'**
  String get feedbackCatTask;

  /// No description provided for @feedbackCatNetwork.
  ///
  /// In en, this message translates to:
  /// **'Network'**
  String get feedbackCatNetwork;

  /// No description provided for @feedbackCatOther.
  ///
  /// In en, this message translates to:
  /// **'Other'**
  String get feedbackCatOther;

  /// No description provided for @feedbackSevLow.
  ///
  /// In en, this message translates to:
  /// **'Low'**
  String get feedbackSevLow;

  /// No description provided for @feedbackSevMedium.
  ///
  /// In en, this message translates to:
  /// **'Medium'**
  String get feedbackSevMedium;

  /// No description provided for @feedbackSevHigh.
  ///
  /// In en, this message translates to:
  /// **'High'**
  String get feedbackSevHigh;

  /// No description provided for @onboardingTitle.
  ///
  /// In en, this message translates to:
  /// **'Field onboarding'**
  String get onboardingTitle;

  /// No description provided for @onboardingIntro.
  ///
  /// In en, this message translates to:
  /// **'Complete these steps before your first pilot day.'**
  String get onboardingIntro;

  /// No description provided for @onboardingLogin.
  ///
  /// In en, this message translates to:
  /// **'Sign in with your officer account'**
  String get onboardingLogin;

  /// No description provided for @onboardingInitialSync.
  ///
  /// In en, this message translates to:
  /// **'Run a full sync on Wi‑Fi'**
  String get onboardingInitialSync;

  /// No description provided for @onboardingReviewTasks.
  ///
  /// In en, this message translates to:
  /// **'Open My Tasks and review assignments'**
  String get onboardingReviewTasks;

  /// No description provided for @onboardingOfflineTest.
  ///
  /// In en, this message translates to:
  /// **'Optional: turn off data and confirm cached views'**
  String get onboardingOfflineTest;

  /// No description provided for @onboardingFeedback.
  ///
  /// In en, this message translates to:
  /// **'Know how to send pilot feedback from the menu'**
  String get onboardingFeedback;

  /// No description provided for @onboardingRequired.
  ///
  /// In en, this message translates to:
  /// **'Recommended'**
  String get onboardingRequired;

  /// No description provided for @onboardingDone.
  ///
  /// In en, this message translates to:
  /// **'Continue to app'**
  String get onboardingDone;

  /// No description provided for @appVersionLabel.
  ///
  /// In en, this message translates to:
  /// **'App version {version}'**
  String appVersionLabel(String version);

  /// No description provided for @navHome.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get navHome;

  /// No description provided for @navFarmers.
  ///
  /// In en, this message translates to:
  /// **'Farmers'**
  String get navFarmers;

  /// No description provided for @dashboardWelcome.
  ///
  /// In en, this message translates to:
  /// **'Welcome, {name}'**
  String dashboardWelcome(String name);

  /// No description provided for @dashboardRoleLine.
  ///
  /// In en, this message translates to:
  /// **'Role: {role}'**
  String dashboardRoleLine(String role);

  /// No description provided for @dashboardBlocksLine.
  ///
  /// In en, this message translates to:
  /// **'Blocks: {blocks}'**
  String dashboardBlocksLine(String blocks);

  /// No description provided for @dashboardProjects.
  ///
  /// In en, this message translates to:
  /// **'Projects'**
  String get dashboardProjects;

  /// No description provided for @dashboardOpenTasks.
  ///
  /// In en, this message translates to:
  /// **'Open tasks'**
  String get dashboardOpenTasks;

  /// No description provided for @dashboardViewFarmers.
  ///
  /// In en, this message translates to:
  /// **'View farmers'**
  String get dashboardViewFarmers;

  /// No description provided for @roleOwner.
  ///
  /// In en, this message translates to:
  /// **'Owner'**
  String get roleOwner;

  /// No description provided for @roleOfficeManager.
  ///
  /// In en, this message translates to:
  /// **'Office Manager'**
  String get roleOfficeManager;

  /// No description provided for @roleFieldStaff.
  ///
  /// In en, this message translates to:
  /// **'Field Staff'**
  String get roleFieldStaff;

  /// No description provided for @roleUser.
  ///
  /// In en, this message translates to:
  /// **'User'**
  String get roleUser;

  /// No description provided for @emptyFarmers.
  ///
  /// In en, this message translates to:
  /// **'No farmers found'**
  String get emptyFarmers;

  /// No description provided for @noProjectForFarmer.
  ///
  /// In en, this message translates to:
  /// **'No active project for this farmer'**
  String get noProjectForFarmer;

  /// No description provided for @projectTimelineTitle.
  ///
  /// In en, this message translates to:
  /// **'Project timeline'**
  String get projectTimelineTitle;

  /// No description provided for @advanceStage.
  ///
  /// In en, this message translates to:
  /// **'Advance to {stage}'**
  String advanceStage(String stage);

  /// No description provided for @stageTransitionSuccess.
  ///
  /// In en, this message translates to:
  /// **'Stage updated — sync to refresh tasks'**
  String get stageTransitionSuccess;

  /// No description provided for @timelineNoteLabel.
  ///
  /// In en, this message translates to:
  /// **'Note'**
  String get timelineNoteLabel;

  /// No description provided for @timelineNoteQueue.
  ///
  /// In en, this message translates to:
  /// **'Queue note'**
  String get timelineNoteQueue;

  /// No description provided for @syncLastRequestId.
  ///
  /// In en, this message translates to:
  /// **'Last request ID'**
  String get syncLastRequestId;

  /// No description provided for @syncRepairQueue.
  ///
  /// In en, this message translates to:
  /// **'Repair queue'**
  String get syncRepairQueue;

  /// No description provided for @taskMaterialsTitle.
  ///
  /// In en, this message translates to:
  /// **'Materials'**
  String get taskMaterialsTitle;

  /// No description provided for @taskConsumeOne.
  ///
  /// In en, this message translates to:
  /// **'Consume 1'**
  String get taskConsumeOne;

  /// No description provided for @notificationTaskDue.
  ///
  /// In en, this message translates to:
  /// **'Task due'**
  String get notificationTaskDue;

  /// No description provided for @notificationTaskOverdue.
  ///
  /// In en, this message translates to:
  /// **'Task overdue'**
  String get notificationTaskOverdue;

  /// No description provided for @notificationStageTransition.
  ///
  /// In en, this message translates to:
  /// **'Stage updated'**
  String get notificationStageTransition;

  /// No description provided for @notificationProjectStatus.
  ///
  /// In en, this message translates to:
  /// **'Project update'**
  String get notificationProjectStatus;

  /// No description provided for @notificationSlaBreach.
  ///
  /// In en, this message translates to:
  /// **'SLA breach'**
  String get notificationSlaBreach;

  /// No description provided for @notificationManual.
  ///
  /// In en, this message translates to:
  /// **'Notification'**
  String get notificationManual;

  /// No description provided for @stageLeadCaptured.
  ///
  /// In en, this message translates to:
  /// **'Lead captured'**
  String get stageLeadCaptured;

  /// No description provided for @stageEligibilityCheck.
  ///
  /// In en, this message translates to:
  /// **'Eligibility check'**
  String get stageEligibilityCheck;

  /// No description provided for @stageDocumentsCollected.
  ///
  /// In en, this message translates to:
  /// **'Documents collected'**
  String get stageDocumentsCollected;

  /// No description provided for @stageMimisRegistered.
  ///
  /// In en, this message translates to:
  /// **'MIMIS registered'**
  String get stageMimisRegistered;

  /// No description provided for @stageFieldSurvey.
  ///
  /// In en, this message translates to:
  /// **'Field survey'**
  String get stageFieldSurvey;

  /// No description provided for @stageQuotationGenerated.
  ///
  /// In en, this message translates to:
  /// **'Quotation generated'**
  String get stageQuotationGenerated;

  /// No description provided for @stagePreInspectionApproval.
  ///
  /// In en, this message translates to:
  /// **'Pre-inspection approval'**
  String get stagePreInspectionApproval;

  /// No description provided for @stageWorkOrderReceived.
  ///
  /// In en, this message translates to:
  /// **'Work order received'**
  String get stageWorkOrderReceived;

  /// No description provided for @stageMaterialDispatched.
  ///
  /// In en, this message translates to:
  /// **'Material dispatched'**
  String get stageMaterialDispatched;

  /// No description provided for @stageInstallationDone.
  ///
  /// In en, this message translates to:
  /// **'Installation done'**
  String get stageInstallationDone;

  /// No description provided for @stagePostInspectionApproval.
  ///
  /// In en, this message translates to:
  /// **'Post-inspection approval'**
  String get stagePostInspectionApproval;

  /// No description provided for @stageSubsidyReleased.
  ///
  /// In en, this message translates to:
  /// **'Subsidy released'**
  String get stageSubsidyReleased;

  /// No description provided for @timelineStageToday.
  ///
  /// In en, this message translates to:
  /// **'TODAY'**
  String get timelineStageToday;

  /// No description provided for @timelineStagePending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get timelineStagePending;

  /// No description provided for @timelineStageLocked.
  ///
  /// In en, this message translates to:
  /// **'Locked'**
  String get timelineStageLocked;

  /// No description provided for @timelineStageBy.
  ///
  /// In en, this message translates to:
  /// **'By {name}'**
  String timelineStageBy(String name);

  /// No description provided for @timelineActionCall.
  ///
  /// In en, this message translates to:
  /// **'Call'**
  String get timelineActionCall;

  /// No description provided for @timelineActionWhatsapp.
  ///
  /// In en, this message translates to:
  /// **'WhatsApp'**
  String get timelineActionWhatsapp;

  /// No description provided for @timelineActionNote.
  ///
  /// In en, this message translates to:
  /// **'Note'**
  String get timelineActionNote;

  /// No description provided for @timelineBlockerMissing.
  ///
  /// In en, this message translates to:
  /// **'Missing: {item}'**
  String timelineBlockerMissing(String item);

  /// No description provided for @timelineHeaderLocation.
  ///
  /// In en, this message translates to:
  /// **'{block} · {village}{acres}'**
  String timelineHeaderLocation(String block, String village, String acres);

  /// No description provided for @timelineHeaderSchemeDrip.
  ///
  /// In en, this message translates to:
  /// **'Drip irrigation · subsidy project'**
  String get timelineHeaderSchemeDrip;

  /// No description provided for @timelineHeaderSchemeSubsidy.
  ///
  /// In en, this message translates to:
  /// **'Subsidy drip project'**
  String get timelineHeaderSchemeSubsidy;

  /// No description provided for @timelineHeaderProject.
  ///
  /// In en, this message translates to:
  /// **'Project {id}'**
  String timelineHeaderProject(String id);

  /// No description provided for @timelineHeaderOfficer.
  ///
  /// In en, this message translates to:
  /// **'Officer: {name}'**
  String timelineHeaderOfficer(String name);

  /// No description provided for @timelineHeaderReferral.
  ///
  /// In en, this message translates to:
  /// **'Referred by: {name}'**
  String timelineHeaderReferral(String name);

  /// No description provided for @timelineAcres.
  ///
  /// In en, this message translates to:
  /// **'acres'**
  String get timelineAcres;

  /// No description provided for @taskFeedTitle.
  ///
  /// In en, this message translates to:
  /// **'Today\'s work'**
  String get taskFeedTitle;

  /// No description provided for @taskFeedSummary.
  ///
  /// In en, this message translates to:
  /// **'{pending} pending · {overdue} overdue'**
  String taskFeedSummary(int pending, int overdue);

  /// No description provided for @taskSectionOverdue.
  ///
  /// In en, this message translates to:
  /// **'Overdue'**
  String get taskSectionOverdue;

  /// No description provided for @taskSectionToday.
  ///
  /// In en, this message translates to:
  /// **'Today'**
  String get taskSectionToday;

  /// No description provided for @taskSectionUpcoming.
  ///
  /// In en, this message translates to:
  /// **'Upcoming'**
  String get taskSectionUpcoming;

  /// No description provided for @taskFeedEmptyCelebration.
  ///
  /// In en, this message translates to:
  /// **'🎉 No pending tasks today!'**
  String get taskFeedEmptyCelebration;

  /// No description provided for @taskFilterAll.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get taskFilterAll;

  /// No description provided for @taskFilterMine.
  ///
  /// In en, this message translates to:
  /// **'My tasks'**
  String get taskFilterMine;

  /// No description provided for @taskFilterVisit.
  ///
  /// In en, this message translates to:
  /// **'Visit'**
  String get taskFilterVisit;

  /// No description provided for @taskFilterDocument.
  ///
  /// In en, this message translates to:
  /// **'Documents'**
  String get taskFilterDocument;

  /// No description provided for @taskDueToday.
  ///
  /// In en, this message translates to:
  /// **'Due today'**
  String get taskDueToday;

  /// No description provided for @taskDueDaysAgo.
  ///
  /// In en, this message translates to:
  /// **'{days} days ago'**
  String taskDueDaysAgo(int days);

  /// No description provided for @taskDueInDays.
  ///
  /// In en, this message translates to:
  /// **'In {days} days'**
  String taskDueInDays(int days);

  /// No description provided for @taskGpsCheckIn.
  ///
  /// In en, this message translates to:
  /// **'GPS check-in at field'**
  String get taskGpsCheckIn;

  /// No description provided for @taskGpsCheckedIn.
  ///
  /// In en, this message translates to:
  /// **'Checked in at field'**
  String get taskGpsCheckedIn;

  /// No description provided for @taskVoiceNoteAttach.
  ///
  /// In en, this message translates to:
  /// **'Attach voice note'**
  String get taskVoiceNoteAttach;

  /// No description provided for @taskVoiceNoteQueued.
  ///
  /// In en, this message translates to:
  /// **'Voice note queued for sync'**
  String get taskVoiceNoteQueued;

  /// No description provided for @notificationMarkAllRead.
  ///
  /// In en, this message translates to:
  /// **'Mark all read'**
  String get notificationMarkAllRead;

  /// No description provided for @notificationEmptyFriendly.
  ///
  /// In en, this message translates to:
  /// **'You\'re all caught up — no new alerts.'**
  String get notificationEmptyFriendly;

  /// No description provided for @notificationFilterAll.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get notificationFilterAll;

  /// No description provided for @notificationFilterUrgent.
  ///
  /// In en, this message translates to:
  /// **'Urgent'**
  String get notificationFilterUrgent;

  /// No description provided for @notificationFilterTasks.
  ///
  /// In en, this message translates to:
  /// **'Tasks'**
  String get notificationFilterTasks;

  /// No description provided for @notificationGroupToday.
  ///
  /// In en, this message translates to:
  /// **'Today'**
  String get notificationGroupToday;

  /// No description provided for @notificationGroupYesterday.
  ///
  /// In en, this message translates to:
  /// **'Yesterday'**
  String get notificationGroupYesterday;

  /// No description provided for @notificationGroupThisWeek.
  ///
  /// In en, this message translates to:
  /// **'This week'**
  String get notificationGroupThisWeek;

  /// No description provided for @notificationGroupOlder.
  ///
  /// In en, this message translates to:
  /// **'Older'**
  String get notificationGroupOlder;

  /// No description provided for @notificationFollowupMissed.
  ///
  /// In en, this message translates to:
  /// **'Missed follow-up'**
  String get notificationFollowupMissed;

  /// No description provided for @notificationStageStuck.
  ///
  /// In en, this message translates to:
  /// **'Stage stuck'**
  String get notificationStageStuck;

  /// No description provided for @notificationOfficerTransfer.
  ///
  /// In en, this message translates to:
  /// **'Officer transfer'**
  String get notificationOfficerTransfer;

  /// No description provided for @notificationLowStock.
  ///
  /// In en, this message translates to:
  /// **'Low stock alert'**
  String get notificationLowStock;

  /// No description provided for @notificationTaskCompleted.
  ///
  /// In en, this message translates to:
  /// **'Task completed'**
  String get notificationTaskCompleted;

  /// No description provided for @syncBarOnline.
  ///
  /// In en, this message translates to:
  /// **'Online · {count} pending'**
  String syncBarOnline(int count);

  /// No description provided for @syncBarOffline.
  ///
  /// In en, this message translates to:
  /// **'Offline · {count} pending'**
  String syncBarOffline(int count);

  /// No description provided for @syncBarSyncing.
  ///
  /// In en, this message translates to:
  /// **'Syncing {current} of {total}…'**
  String syncBarSyncing(int current, int total);

  /// No description provided for @syncBarJustSynced.
  ///
  /// In en, this message translates to:
  /// **'All synced just now'**
  String get syncBarJustSynced;

  /// No description provided for @syncBarTapHintOnline.
  ///
  /// In en, this message translates to:
  /// **'Tap Sync tab to force refresh'**
  String get syncBarTapHintOnline;

  /// No description provided for @syncBarTapHintOffline.
  ///
  /// In en, this message translates to:
  /// **'Changes saved locally — sync when online'**
  String get syncBarTapHintOffline;

  /// No description provided for @syncToastSavedOffline.
  ///
  /// In en, this message translates to:
  /// **'Saved offline ✓'**
  String get syncToastSavedOffline;

  /// No description provided for @syncToastComplete.
  ///
  /// In en, this message translates to:
  /// **'Synced ✓'**
  String get syncToastComplete;

  /// No description provided for @syncToastStarted.
  ///
  /// In en, this message translates to:
  /// **'Syncing your changes…'**
  String get syncToastStarted;

  /// No description provided for @syncForceNow.
  ///
  /// In en, this message translates to:
  /// **'Force sync now'**
  String get syncForceNow;

  /// No description provided for @syncLastSuccessLabel.
  ///
  /// In en, this message translates to:
  /// **'Last successful sync: {time}'**
  String syncLastSuccessLabel(String time);

  /// No description provided for @syncPendingChanges.
  ///
  /// In en, this message translates to:
  /// **'Pending changes: {count} items'**
  String syncPendingChanges(int count);

  /// No description provided for @syncPendingListTitle.
  ///
  /// In en, this message translates to:
  /// **'Pending queue'**
  String get syncPendingListTitle;

  /// No description provided for @syncPendingListEmpty.
  ///
  /// In en, this message translates to:
  /// **'No pending changes in queue'**
  String get syncPendingListEmpty;

  /// No description provided for @syncHistoryTitle.
  ///
  /// In en, this message translates to:
  /// **'Sync history (last 10)'**
  String get syncHistoryTitle;

  /// No description provided for @syncHistoryEmpty.
  ///
  /// In en, this message translates to:
  /// **'No sync runs logged yet'**
  String get syncHistoryEmpty;

  /// No description provided for @syncHistoryOk.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get syncHistoryOk;

  /// No description provided for @syncHistoryFail.
  ///
  /// In en, this message translates to:
  /// **'Failed'**
  String get syncHistoryFail;

  /// No description provided for @syncDeveloperTitle.
  ///
  /// In en, this message translates to:
  /// **'Developer (demo)'**
  String get syncDeveloperTitle;

  /// No description provided for @syncSimulateOffline.
  ///
  /// In en, this message translates to:
  /// **'Simulate offline'**
  String get syncSimulateOffline;

  /// No description provided for @syncSimulateOfflineHint.
  ///
  /// In en, this message translates to:
  /// **'Queue writes without network — for live demo'**
  String get syncSimulateOfflineHint;

  /// No description provided for @syncSimulateOfflineOn.
  ///
  /// In en, this message translates to:
  /// **'Simulated offline ON'**
  String get syncSimulateOfflineOn;

  /// No description provided for @syncSimulateOfflineOff.
  ///
  /// In en, this message translates to:
  /// **'Simulated offline OFF'**
  String get syncSimulateOfflineOff;

  /// No description provided for @syncDemoFlowButton.
  ///
  /// In en, this message translates to:
  /// **'Demo: go online & sync'**
  String get syncDemoFlowButton;

  /// No description provided for @syncNever.
  ///
  /// In en, this message translates to:
  /// **'Never'**
  String get syncNever;

  /// No description provided for @syncJustNow.
  ///
  /// In en, this message translates to:
  /// **'Just now'**
  String get syncJustNow;

  /// No description provided for @syncMinutesAgo.
  ///
  /// In en, this message translates to:
  /// **'{minutes} min ago'**
  String syncMinutesAgo(int minutes);

  /// No description provided for @syncHoursAgo.
  ///
  /// In en, this message translates to:
  /// **'{hours} hr ago'**
  String syncHoursAgo(int hours);

  /// No description provided for @sectionWithCount.
  ///
  /// In en, this message translates to:
  /// **'{label} ({count})'**
  String sectionWithCount(String label, int count);

  /// No description provided for @syncFlyingItem.
  ///
  /// In en, this message translates to:
  /// **'Upload {index}'**
  String syncFlyingItem(int index);

  /// No description provided for @conflictStepNumbered.
  ///
  /// In en, this message translates to:
  /// **'{step}. {text}'**
  String conflictStepNumbered(int step, String text);

  /// No description provided for @conflictMutationId.
  ///
  /// In en, this message translates to:
  /// **'Mutation: {id}'**
  String conflictMutationId(String id);

  /// No description provided for @conflictVersionLine.
  ///
  /// In en, this message translates to:
  /// **'Server v{server} · Client v{client}'**
  String conflictVersionLine(int server, int client);

  /// No description provided for @conflictCodeDefault.
  ///
  /// In en, this message translates to:
  /// **'Sync conflict'**
  String get conflictCodeDefault;

  /// No description provided for @syncQueueItemTitle.
  ///
  /// In en, this message translates to:
  /// **'{entity} · {op}'**
  String syncQueueItemTitle(String entity, String op);

  /// No description provided for @taskFarmerVillageLine.
  ///
  /// In en, this message translates to:
  /// **'{farmer} · {village}'**
  String taskFarmerVillageLine(String farmer, String village);

  /// No description provided for @taskStatusProjectLine.
  ///
  /// In en, this message translates to:
  /// **'{status} · {project}'**
  String taskStatusProjectLine(String status, String project);

  /// No description provided for @taskReservedQty.
  ///
  /// In en, this message translates to:
  /// **'Reserved {qty} · {status}'**
  String taskReservedQty(String qty, String status);

  /// No description provided for @updateRequiredMessage.
  ///
  /// In en, this message translates to:
  /// **'Update required (minimum {version})'**
  String updateRequiredMessage(String version);

  /// No description provided for @stageSecondaryDocsComplete.
  ///
  /// In en, this message translates to:
  /// **'4/4 documents uploaded'**
  String get stageSecondaryDocsComplete;

  /// No description provided for @stageSecondaryMimisId.
  ///
  /// In en, this message translates to:
  /// **'ID: {id}'**
  String stageSecondaryMimisId(String id);

  /// No description provided for @stageSecondaryQuotation.
  ///
  /// In en, this message translates to:
  /// **'₹{amount}'**
  String stageSecondaryQuotation(String amount);

  /// No description provided for @stageSecondaryAaoApproved.
  ///
  /// In en, this message translates to:
  /// **'AAO approved'**
  String get stageSecondaryAaoApproved;

  /// No description provided for @stageSecondaryStockReserved.
  ///
  /// In en, this message translates to:
  /// **'Stock reserved'**
  String get stageSecondaryStockReserved;

  /// No description provided for @stageSecondaryInstallationTeam.
  ///
  /// In en, this message translates to:
  /// **'Murugan installation team'**
  String get stageSecondaryInstallationTeam;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'ta'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'ta':
      return AppLocalizationsTa();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
