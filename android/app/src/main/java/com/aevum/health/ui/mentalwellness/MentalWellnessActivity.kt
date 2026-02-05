package com.aevum.health.ui.mentalwellness

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.aevum.health.databinding.ActivityMentalWellnessBinding

class MentalWellnessActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMentalWellnessBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMentalWellnessBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Enable back button
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Mental Wellness"
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}

