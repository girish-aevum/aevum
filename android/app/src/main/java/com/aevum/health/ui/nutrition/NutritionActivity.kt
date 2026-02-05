package com.aevum.health.ui.nutrition

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.aevum.health.databinding.ActivityNutritionBinding

class NutritionActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityNutritionBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityNutritionBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Enable back button
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Nutrition"
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}

