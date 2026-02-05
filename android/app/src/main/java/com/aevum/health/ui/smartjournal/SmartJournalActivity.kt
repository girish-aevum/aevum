package com.aevum.health.ui.smartjournal

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import com.aevum.health.R
import com.aevum.health.data.models.CreateJournalEntryRequest
import com.aevum.health.data.models.JournalCategory
import com.aevum.health.data.models.JournalEntry
import com.aevum.health.data.models.JournalEntryDetail
import com.aevum.health.data.models.JournalInsight
import com.aevum.health.data.models.JournalReminder
import com.aevum.health.data.models.JournalStreak
import com.aevum.health.data.models.JournalTemplate
import com.aevum.health.data.models.Milestone
import com.aevum.health.data.models.QuickJournalEntryRequest
import com.aevum.health.databinding.ActivitySmartJournalBinding
import com.aevum.health.databinding.DialogJournalEntryDetailBinding
import com.aevum.health.databinding.DialogNewJournalEntryBinding
import com.aevum.health.network.RetrofitClient
import com.aevum.health.repository.AuthRepository
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.chip.Chip
import kotlinx.coroutines.async
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.DateTimeFormatter

class SmartJournalActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySmartJournalBinding
    private lateinit var authRepository: AuthRepository
    private lateinit var entriesAdapter: JournalEntriesAdapter
    private lateinit var insightsAdapter: JournalInsightsAdapter
    private lateinit var calendarAdapter: JournalCalendarAdapter

    private var categories: List<JournalCategory> = emptyList()
    private var templates: List<JournalTemplate> = emptyList()
    private var currentMonth: YearMonth = YearMonth.now()
    private var monthEntries: List<JournalEntry> = emptyList()

    private val monthFormatter = DateTimeFormatter.ofPattern("MMMM yyyy")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySmartJournalBinding.inflate(layoutInflater)
        setContentView(binding.root)

        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Smart Journal"

        authRepository = AuthRepository(this)

        setupAdapters()
        setupListeners()
        loadSmartJournalDashboard()
        loadCalendarEntries()
    }

    private fun setupAdapters() {
        entriesAdapter = JournalEntriesAdapter { entry ->
            entry.entryId?.let { showEntryDetail(it) }
        }
        insightsAdapter = JournalInsightsAdapter()
        calendarAdapter = JournalCalendarAdapter { date, entries ->
            showEntriesForDate(date, entries)
        }

        binding.rvJournalEntries.apply {
            layoutManager = LinearLayoutManager(this@SmartJournalActivity)
            adapter = entriesAdapter
        }

        binding.rvInsights.apply {
            layoutManager = LinearLayoutManager(this@SmartJournalActivity)
            adapter = insightsAdapter
        }

        binding.rvCalendar.apply {
            layoutManager = GridLayoutManager(this@SmartJournalActivity, 7)
            adapter = calendarAdapter
        }
    }

    private fun setupListeners() {
        binding.btnNewEntry.setOnClickListener { showNewEntryDialog() }
        binding.btnAddQuickEntry.setOnClickListener { handleQuickEntry() }
        binding.btnViewAllEntries.setOnClickListener {
            Toast.makeText(this, "Full entries view coming soon.", Toast.LENGTH_SHORT).show()
        }
        binding.btnPreviousMonth.setOnClickListener {
            currentMonth = currentMonth.minusMonths(1)
            updateMonthLabel()
            loadCalendarEntries()
        }
        binding.btnNextMonth.setOnClickListener {
            currentMonth = currentMonth.plusMonths(1)
            updateMonthLabel()
            loadCalendarEntries()
        }
        binding.sliderQuickMood.addOnChangeListener { _, value, _ ->
            binding.tvQuickMoodLabel.text = "Mood: ${moodLabel(value.toInt())}"
        }
        updateMonthLabel()
    }

    private fun loadSmartJournalDashboard() {
        lifecycleScope.launch {
            val token = authRepository.getAccessToken()
            if (token.isNullOrBlank()) {
                Toast.makeText(this@SmartJournalActivity, "Please login to view Smart Journal.", Toast.LENGTH_SHORT).show()
                return@launch
            }

            val apiService = RetrofitClient.createApiServiceWithToken(token)
            binding.progressSmartJournal.isVisible = true

            try {
                val entriesDeferred = async { apiService.getJournalEntries(limit = 5) }
                val streakDeferred = async { apiService.getJournalStreak() }
                val remindersDeferred = async { apiService.getJournalReminders() }
                val insightsDeferred = async { apiService.getJournalInsights(limit = 4) }
                val categoriesDeferred = async { apiService.getJournalCategories(limit = 100) }
                val templatesDeferred = async { apiService.getJournalTemplates(limit = 100) }

                val entriesResponse = entriesDeferred.await()
                if (entriesResponse.isSuccessful) {
                    val entries: List<JournalEntry> = entriesResponse.body()?.results ?: emptyList()
                    entriesAdapter.submitList(entries)
                    binding.tvNoEntries.isVisible = entries.isEmpty()
                } else {
                    binding.tvNoEntries.isVisible = true
                }

                val streakResponse = streakDeferred.await()
                val reminderResponse = remindersDeferred.await()
                if (streakResponse.isSuccessful) {
                    val streak = streakResponse.body()
                    val reminder = reminderResponse.body()?.results?.firstOrNull()
                    updateSnapshotCard(streak, reminder)
                }

                val insightsResponse = insightsDeferred.await()
                if (insightsResponse.isSuccessful) {
                    val insights: List<JournalInsight> = insightsResponse.body()?.results ?: emptyList()
                    insightsAdapter.submitList(insights)
                    binding.tvNoInsights.isVisible = insights.isEmpty()
                } else {
                    binding.tvNoInsights.isVisible = true
                }

                val categoriesResponse = categoriesDeferred.await()
                if (categoriesResponse.isSuccessful) {
                    categories = categoriesResponse.body()?.results ?: emptyList()
                }

                val templatesResponse = templatesDeferred.await()
                if (templatesResponse.isSuccessful) {
                    templates = templatesResponse.body()?.results ?: emptyList()
                }
            } catch (e: Exception) {
                Toast.makeText(this@SmartJournalActivity, "Failed to load Smart Journal: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                binding.progressSmartJournal.isVisible = false
            }
        }
    }

    private fun loadCalendarEntries() {
        lifecycleScope.launch {
            val token = authRepository.getAccessToken() ?: return@launch
            val apiService = RetrofitClient.createApiServiceWithToken(token)
            val startDate = currentMonth.atDay(1).toString()
            val endDate = currentMonth.atEndOfMonth().toString()

            try {
                val response = apiService.getJournalEntries(
                    pageSize = 200,
                    limit = 200,
                    startDate = startDate,
                    endDate = endDate
                )
                if (response.isSuccessful) {
                    monthEntries = response.body()?.results ?: emptyList()
                    calendarAdapter.submitList(buildCalendarDays(monthEntries))
                }
            } catch (e: Exception) {
                Toast.makeText(this@SmartJournalActivity, "Failed to load calendar data", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun buildCalendarDays(entries: List<JournalEntry>): List<CalendarDay> {
        val days = mutableListOf<CalendarDay>()
        val firstDay = currentMonth.atDay(1)
        val startOffset = (firstDay.dayOfWeek.value % 7)
        val totalDays = currentMonth.lengthOfMonth()
        val totalCells = ((startOffset + totalDays + 6) / 7) * 7

        for (i in 0 until totalCells) {
            val dayNumber = i - startOffset + 1
            if (dayNumber < 1 || dayNumber > totalDays) {
                days.add(CalendarDay(null))
            } else {
                val date = currentMonth.atDay(dayNumber)
                val dayEntries = entries.filter { it.entryDate == date.toString() }
                days.add(CalendarDay(date, dayEntries))
            }
        }
        return days
    }

    private fun updateMonthLabel() {
        binding.tvMonthYear.text = currentMonth.format(monthFormatter)
    }

    private fun handleQuickEntry() {
        val text = binding.etQuickEntry.text?.toString()?.trim().orEmpty()
        if (text.isEmpty()) {
            Toast.makeText(this, "Write a quick thought first.", Toast.LENGTH_SHORT).show()
            return
        }

        lifecycleScope.launch {
            val token = authRepository.getAccessToken() ?: return@launch
            val apiService = RetrofitClient.createApiServiceWithToken(token)
            try {
                binding.btnAddQuickEntry.isEnabled = false
                apiService.createQuickJournalEntry(
                    QuickJournalEntryRequest(
                        content = text,
                        moodRating = binding.sliderQuickMood.value.toInt()
                    )
                )
                binding.etQuickEntry.setText("")
                loadSmartJournalDashboard()
                loadCalendarEntries()
                Toast.makeText(this@SmartJournalActivity, "Entry saved!", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Toast.makeText(this@SmartJournalActivity, "Failed to save entry: ${e.message}", Toast.LENGTH_SHORT).show()
            } finally {
                binding.btnAddQuickEntry.isEnabled = true
            }
        }
    }

    private fun showNewEntryDialog() {
        val dialogBinding = DialogNewJournalEntryBinding.inflate(LayoutInflater.from(this))
        val dialog = BottomSheetDialog(this)
        dialog.setContentView(dialogBinding.root)

        setupDropdowns(dialogBinding)

        dialogBinding.sliderMood.addOnChangeListener { _, value, _ ->
            dialogBinding.tvMoodValue.text = "Mood: ${moodLabel(value.toInt())}"
        }

        dialogBinding.sliderEnergy.addOnChangeListener { _, value, _ ->
            dialogBinding.tvEnergyValue.text = "Energy: ${energyLabel(value.toInt())}"
        }

        dialogBinding.btnSaveEntry.setOnClickListener {
            val title = dialogBinding.etEntryTitle.text?.toString()?.trim().orEmpty()
            val content = dialogBinding.etEntryContent.text?.toString()?.trim().orEmpty()
            if (title.isEmpty() || content.isEmpty()) {
                Toast.makeText(this, "Title and content are required.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val tags = dialogBinding.etEntryTags.text?.toString()
                ?.split(",")
                ?.map { it.trim() }
                ?.filter { it.isNotEmpty() }
                ?: emptyList()

            val categoryId = dialogBinding.actCategory.tag as? Int
            val templateId = dialogBinding.actTemplate.tag as? Int
            val privacyCode = dialogBinding.actPrivacy.tag as? String ?: "PRIVATE"

            val request = CreateJournalEntryRequest(
                title = title,
                content = content,
                moodRating = dialogBinding.sliderMood.value.toInt(),
                energyLevel = dialogBinding.sliderEnergy.value.toInt(),
                privacyLevel = privacyCode,
                isFavorite = dialogBinding.switchFavorite.isChecked,
                isDraft = dialogBinding.switchDraft.isChecked,
                tagNames = tags,
                category = categoryId,
                template = templateId,
                location = dialogBinding.etEntryLocation.text?.toString(),
                weather = dialogBinding.etEntryWeather.text?.toString()
            )

            lifecycleScope.launch {
                val token = authRepository.getAccessToken() ?: return@launch
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                try {
                    dialogBinding.pbEntrySubmit.isVisible = true
                    dialogBinding.btnSaveEntry.isEnabled = false
                    val response = apiService.createJournalEntry(request)
                    if (response.isSuccessful) {
                        Toast.makeText(this@SmartJournalActivity, "Entry created!", Toast.LENGTH_SHORT).show()
                        dialog.dismiss()
                        loadSmartJournalDashboard()
                        loadCalendarEntries()
                    } else {
                        Toast.makeText(this@SmartJournalActivity, "Failed to create entry.", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@SmartJournalActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                } finally {
                    dialogBinding.pbEntrySubmit.isVisible = false
                    dialogBinding.btnSaveEntry.isEnabled = true
                }
            }
        }

        dialog.show()
    }

    private fun setupDropdowns(dialogBinding: DialogNewJournalEntryBinding) {
        val categoryNames = categories.map { it.name ?: "Category" }
        dialogBinding.actCategory.setAdapter(
            ArrayAdapter(this, android.R.layout.simple_list_item_1, categoryNames)
        )
        dialogBinding.actCategory.setOnItemClickListener { _, _, position, _ ->
            dialogBinding.actCategory.tag = categories.getOrNull(position)?.id
        }

        val templateNames = templates.map { it.name ?: "Template" }
        dialogBinding.actTemplate.setAdapter(
            ArrayAdapter(this, android.R.layout.simple_list_item_1, templateNames)
        )
        dialogBinding.actTemplate.setOnItemClickListener { _, _, position, _ ->
            dialogBinding.actTemplate.tag = templates.getOrNull(position)?.id
        }

        val privacyOptions = listOf(
            "PRIVATE" to "Private (Only Me)",
            "SHARED" to "Shared",
            "PUBLIC" to "Public"
        )
        dialogBinding.actPrivacy.setAdapter(
            ArrayAdapter(this, android.R.layout.simple_list_item_1, privacyOptions.map { it.second })
        )
        dialogBinding.actPrivacy.setOnItemClickListener { _, _, position, _ ->
            dialogBinding.actPrivacy.tag = privacyOptions[position].first
        }
        dialogBinding.actPrivacy.setText(privacyOptions.first().second, false)
        dialogBinding.actPrivacy.tag = privacyOptions.first().first
    }

    private fun showEntryDetail(entryId: String) {
        lifecycleScope.launch {
            val token = authRepository.getAccessToken() ?: return@launch
            val apiService = RetrofitClient.createApiServiceWithToken(token)
            try {
                val response = apiService.getJournalEntryDetail(entryId)
                if (response.isSuccessful) {
                    response.body()?.let { displayEntryDetail(it) }
                } else {
                    Toast.makeText(this@SmartJournalActivity, "Failed to load entry detail.", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@SmartJournalActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun displayEntryDetail(detail: JournalEntryDetail) {
        val dialogBinding = DialogJournalEntryDetailBinding.inflate(LayoutInflater.from(this))
        val dialog = BottomSheetDialog(this)
        dialog.setContentView(dialogBinding.root)

        dialogBinding.tvDetailTitle.text = detail.title ?: "Untitled Entry"
        dialogBinding.tvDetailDate.text = formatIsoDate(detail.entryDate)
        dialogBinding.tvDetailMood.text = "Mood: ${detail.moodEmoji ?: "😐"}"
        dialogBinding.tvDetailEnergy.text = "Energy: ${detail.energyEmoji ?: "🔋🔋🔋"}"
        dialogBinding.tvDetailCategory.text = "Category: ${detail.category?.name ?: "Uncategorized"}"
        dialogBinding.tvDetailLocation.text = "Location: ${detail.location ?: "N/A"}"
        dialogBinding.tvDetailTags.text = "Tags: ${detail.tags?.joinToString { it.name ?: "" } ?: "None"}"
        dialogBinding.tvDetailContent.text = detail.content ?: ""

        dialog.show()
    }

    private fun showEntriesForDate(date: LocalDate, entries: List<JournalEntry>) {
        if (entries.isEmpty()) return
        val builder = StringBuilder()
        builder.append("Entries on ${date.format(DateTimeFormatter.ofPattern("MMM dd, yyyy"))}\n\n")
        entries.forEach {
            builder.append("• ${it.title ?: "Untitled"} (${it.moodEmoji ?: "😐"})\n")
        }
        Toast.makeText(this, builder.toString(), Toast.LENGTH_LONG).show()
    }

    private fun updateSnapshotCard(streak: JournalStreak?, reminder: JournalReminder?) {
        binding.tvCurrentStreak.text = (streak?.currentStreak ?: 0).toString()
        binding.tvLongestStreak.text = (streak?.longestStreak ?: 0).toString()
        binding.tvTotalEntries.text = (streak?.totalEntries ?: 0).toString()
        binding.tvStreakStatus.text = streak?.streakStatus ?: "Start writing to build a streak."
        binding.tvNextReminder.text = reminder?.let {
            "Next reminder: ${it.reminderTime ?: ""} ${it.nextReminderDisplay ?: ""}".trim()
        } ?: "Next reminder: Not scheduled"
        updateMilestones(streak?.milestonesAchieved)
    }

    private fun updateMilestones(milestones: List<Milestone>?) {
        binding.chipMilestones.removeAllViews()
        milestones.orEmpty().takeLast(3).forEach { milestone ->
            val chip = Chip(this).apply {
                text = milestone.milestone ?: "Milestone"
                isCheckable = false
                isClickable = false
            }
            binding.chipMilestones.addView(chip)
        }
    }

    private fun formatIsoDate(date: String?): String {
        if (date.isNullOrBlank()) return "-"
        return try {
            val parsed = LocalDate.parse(date)
            parsed.format(DateTimeFormatter.ofPattern("MMM dd, yyyy"))
        } catch (e: Exception) {
            date
        }
    }

    private fun moodLabel(value: Int): String = when (value) {
        1 -> "😞 Very Sad"
        2 -> "😕 Sad"
        3 -> "😐 Neutral"
        4 -> "😊 Happy"
        5 -> "😄 Very Happy"
        else -> "😐 Neutral"
    }

    private fun energyLabel(value: Int): String = when (value) {
        1 -> "🔋 Very Low"
        2 -> "🔋🔋 Low"
        3 -> "🔋🔋🔋 Moderate"
        4 -> "🔋🔋🔋🔋 High"
        5 -> "🔋🔋🔋🔋🔋 Very High"
        else -> "🔋🔋🔋 Moderate"
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}

