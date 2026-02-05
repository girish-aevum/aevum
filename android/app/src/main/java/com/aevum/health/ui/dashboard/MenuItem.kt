package com.aevum.health.ui.dashboard

data class MenuItem(
    val id: String,
    val title: String,
    val description: String,
    val icon: String, // Emoji or icon text
    val action: () -> Unit
)

