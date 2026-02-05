package com.aevum.health.ui.smartjournal

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.aevum.health.data.models.JournalEntry
import com.aevum.health.data.models.JournalInsight
import com.aevum.health.databinding.ItemCalendarDayBinding
import com.aevum.health.databinding.ItemJournalEntryBinding
import com.aevum.health.databinding.ItemJournalInsightBinding
import com.google.android.material.chip.Chip
import java.time.LocalDate

class JournalEntriesAdapter(
    private val onEntryClick: (JournalEntry) -> Unit
) : ListAdapter<JournalEntry, JournalEntriesAdapter.EntryViewHolder>(DIFF_CALLBACK) {

    companion object {
        private val DIFF_CALLBACK = object : DiffUtil.ItemCallback<JournalEntry>() {
            override fun areItemsTheSame(oldItem: JournalEntry, newItem: JournalEntry): Boolean =
                oldItem.entryId == newItem.entryId

            override fun areContentsTheSame(oldItem: JournalEntry, newItem: JournalEntry): Boolean =
                oldItem == newItem
        }
    }

    inner class EntryViewHolder(private val binding: ItemJournalEntryBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(entry: JournalEntry) {
            binding.tvEntryTitle.text = entry.title ?: "Untitled Entry"
            binding.tvEntryMood.text = entry.moodEmoji ?: "😐"
            binding.tvEntryDate.text = entry.daysAgo ?: entry.entryDate ?: ""
            binding.tvEntryContent.text = entry.contentPreview ?: ""
            binding.tvEntryFavorite.visibility = if (entry.isFavorite == true) View.VISIBLE else View.GONE

            // Tags
            binding.chipGroupTags.removeAllViews()
            val tags = entry.tags ?: emptyList()
            if (tags.isEmpty()) {
                binding.chipGroupTags.visibility = View.GONE
            } else {
                binding.chipGroupTags.visibility = View.VISIBLE
                tags.take(3).forEach { tag ->
                    val chip = Chip(binding.root.context).apply {
                        text = if (tag.length > 15) "${tag.take(15)}..." else tag
                        isCheckable = false
                        isClickable = false
                        setTextSize(11f)
                        chipMinHeight = 0f
                        setPadding(8, 4, 8, 4)
                    }
                    binding.chipGroupTags.addView(chip)
                }
            }

            binding.root.setOnClickListener { onEntryClick(entry) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EntryViewHolder {
        val binding = ItemJournalEntryBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return EntryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: EntryViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

class JournalInsightsAdapter :
    ListAdapter<JournalInsight, JournalInsightsAdapter.InsightViewHolder>(INSIGHT_DIFF) {

    companion object {
        private val INSIGHT_DIFF = object : DiffUtil.ItemCallback<JournalInsight>() {
            override fun areItemsTheSame(oldItem: JournalInsight, newItem: JournalInsight): Boolean =
                oldItem.id == newItem.id

            override fun areContentsTheSame(oldItem: JournalInsight, newItem: JournalInsight): Boolean =
                oldItem == newItem
        }
    }

    inner class InsightViewHolder(private val binding: ItemJournalInsightBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(insight: JournalInsight) {
            binding.tvInsightTitle.text = insight.title ?: "Insight"
            binding.tvInsightType.text = insight.insightTypeDisplay ?: ""
            binding.tvInsightDescription.text = insight.description ?: ""
            binding.tvInsightDate.text = insight.generatedAt?.let { formatDateText(it) }
                ?: ""
        }

        private fun formatDateText(isoDate: String): String {
            return try {
                isoDate.substring(0, 10)
            } catch (e: Exception) {
                isoDate
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): InsightViewHolder {
        val binding = ItemJournalInsightBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return InsightViewHolder(binding)
    }

    override fun onBindViewHolder(holder: InsightViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

data class CalendarDay(
    val date: LocalDate?,
    val entries: List<JournalEntry> = emptyList()
)

class JournalCalendarAdapter(
    private val onDaySelected: (LocalDate, List<JournalEntry>) -> Unit
) : ListAdapter<CalendarDay, JournalCalendarAdapter.CalendarViewHolder>(CALENDAR_DIFF) {

    companion object {
        private val CALENDAR_DIFF = object : DiffUtil.ItemCallback<CalendarDay>() {
            override fun areItemsTheSame(oldItem: CalendarDay, newItem: CalendarDay): Boolean =
                oldItem.date == newItem.date

            override fun areContentsTheSame(oldItem: CalendarDay, newItem: CalendarDay): Boolean =
                oldItem == newItem
        }
    }

    inner class CalendarViewHolder(private val binding: ItemCalendarDayBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(day: CalendarDay) {
            val date = day.date
            if (date == null) {
                binding.containerDay.alpha = 0.2f
                binding.tvCalendarDayNumber.text = ""
                binding.tvCalendarMood.visibility = View.GONE
                binding.tvCalendarEntryCount.visibility = View.GONE
                binding.root.setOnClickListener(null)
                return
            }

            binding.containerDay.alpha = 1f
            binding.tvCalendarDayNumber.text = date.dayOfMonth.toString()

            val hasEntries = day.entries.isNotEmpty()
            if (hasEntries) {
                binding.tvCalendarMood.text = day.entries.firstOrNull()?.moodEmoji ?: "😐"
                binding.tvCalendarMood.visibility = View.VISIBLE
                binding.tvCalendarEntryCount.visibility = View.VISIBLE
                binding.tvCalendarEntryCount.text = "${day.entries.size} entries"
            } else {
                binding.tvCalendarMood.visibility = View.GONE
                binding.tvCalendarEntryCount.visibility = View.GONE
            }

            val isToday = date == LocalDate.now()
            binding.containerDay.setBackgroundResource(
                if (isToday) com.aevum.health.R.drawable.bg_status_completed else android.R.color.transparent
            )

            binding.root.setOnClickListener {
                if (hasEntries) {
                    onDaySelected(date, day.entries)
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CalendarViewHolder {
        val binding = ItemCalendarDayBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return CalendarViewHolder(binding)
    }

    override fun onBindViewHolder(holder: CalendarViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

