# Implementation Plan: BharatSignal

## Overview

This implementation plan converts the BharatSignal design into discrete coding tasks for building an AI-powered decision-support system for kirana shops. The approach focuses on a simple Python backend with HTML interface, Amazon Bedrock integration, and in-memory data processing.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python Flask application structure
  - Set up requirements.txt with Flask, boto3, and CSV processing dependencies
  - Create basic directory structure (templates, static, app modules)
  - Configure AWS credentials and Bedrock access
  - _Requirements: 7.1, 8.1_

- [x] 2. Implement core data models and CSV processing
  - [x] 2.1 Create SalesRecord and LocalContext data classes
    - Write Python dataclasses for sales records and context
    - Implement basic validation methods for data integrity
    - _Requirements: 1.4, 1.5_

  - [x] 2.2 Implement CSV parsing and validation functions
    - Write parse_csv function to convert uploaded files to SalesRecord objects
    - Implement validation for required columns and data types
    - Handle malformed CSV data with clear error messages
    - _Requirements: 1.1, 1.2_

  - [x] 2.3 Manual verification of CSV processing
    - Test with sample CSV files to verify parsing works correctly
    - Verify error messages display for invalid files
    - _Requirements: 1.1, 1.2_

- [x] 3. Create Amazon Bedrock integration
  - [x] 3.1 Implement Bedrock client and authentication
    - Set up boto3 Bedrock client with AWS IAM authentication
    - Configure region and model selection (Claude 3 Sonnet)
    - _Requirements: 2.4, 7.1_

  - [x] 3.2 Build prompt engineering and AI interaction
    - Create prompt templates for kirana shop context
    - Implement prompt building from sales data and local context
    - Write function to invoke Bedrock model and parse responses
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.3 Manual verification of AI integration
    - Test Bedrock connection with sample data
    - Verify recommendations are generated and formatted correctly
    - _Requirements: 2.1, 2.2, 2.3_
    - Parse AI model responses into structured Recommendation objects
    - Format recommendations for display with simple language
    - _Requirements: 2.5, 4.1, 4.2_

  - [x] 3.4 Implement recommendation parsing and formatting
    - Parse AI model responses into structured Recommendation objects
    - Format recommendations for display with simple language
    - _Requirements: 2.5, 4.1, 4.2_

- [ ] 4. Checkpoint - Core AI functionality working
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Build web interface and Flask routes
  - [x] 5.1 Create HTML templates for single-page interface
    - Build index.html with file upload, context input, and results sections
    - Create simple CSS for basic styling and usability
    - _Requirements: 6.1, 6.2_

  - [x] 5.2 Implement Flask routes for file upload and processing
    - Create route for main page rendering
    - Implement /analyze POST route for CSV upload and context processing
    - Handle file upload, CSV parsing, and AI recommendation generation
    - _Requirements: 1.1, 1.3, 3.5_

  - [x] 5.3 Manual verification of recommendation quality
    - Test that recommendations include clear explanations
    - Verify language is simple and accessible
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 5.4 Implement results display and error handling
    - Create results.html template for displaying recommendations
    - Add error handling for invalid uploads and Bedrock failures
    - Display clear error messages to users
    - _Requirements: 6.4, 8.3_

  - [x] 5.5 Manual verification of user interface
    - Test file upload and visual feedback
    - Verify error messages display correctly
    - _Requirements: 6.3_

- [x] 6. Add demo mode and sample data
  - [x] 6.1 Create sample CSV files and demo data
    - Generate representative kirana shop sales data samples
    - Create sample context scenarios (festivals, weather, events)
    - _Requirements: 9.1, 9.2_

  - [x] 6.2 Implement demo mode functionality
    - Add demo mode toggle to pre-populate data
    - Ensure demo mode clearly distinguishes from real data
    - _Requirements: 9.4, 9.5_

  - [-] 6.3 Manual verification of demo mode
    - Test demo mode generates meaningful recommendations
    - Verify demo mode is clearly distinguished from real data
    - _Requirements: 9.3_

- [ ] 7. Implement security and data handling
  - [ ] 7.1 Ensure secure communication assumptions (HTTPS when deployed)
    - Document secure communication requirements
    - Ensure encrypted communication with Bedrock
    - _Requirements: 7.3_

  - [ ] 7.2 Implement session data cleanup
    - Clear uploaded data after processing
    - Ensure no persistent storage of user sales data
    - _Requirements: 7.2, 7.5_

  - [ ] 7.3 Manual verification of data handling
    - Verify uploaded data is cleared after processing
    - Test that no persistent storage occurs
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [ ] 8. Add language support and terminology
  - [ ] 8.1 Implement English output with Indian retail terminology
    - Ensure AI prompts generate appropriate terminology for Indian context
    - Validate output uses simple, accessible English
    - _Requirements: 5.3, 5.4_

  - [ ] 8.2 Add optional Hindi support in prompts only
    - Create Hindi prompt templates for AI responses
    - No UI language selection needed for prototype
    - _Requirements: 5.2_

  - [ ] 8.3 Manual verification of language output
    - Test that AI generates appropriate Indian retail terminology
    - Verify output uses simple, accessible English
    - _Requirements: 5.2, 5.3, 5.4_

- [ ] 9. Performance optimization and reliability
  - [ ] 9.1 Implement basic error handling and logging
    - Add basic error handling for major failure points
    - Add simple logging without exposing user data
    - _Requirements: 8.5_

  - [ ] 9.2 Demo-time observation of performance
    - Observe CSV processing and Bedrock response times during demo
    - Ensure reasonable response times for typical files
    - _Requirements: 3.5, 8.4_

  - [ ] 9.3 Manual verification of system reliability
    - Test error handling with invalid inputs
    - Verify error messages are clear and helpful
    - _Requirements: 8.1, 8.3, 8.5_

- [ ] 10. Final integration and testing
  - [ ] 10.1 Implement context integration in AI recommendations
    - Ensure local context (festivals, weather, events) influences AI recommendations
    - Validate that recommendations reference contextual factors appropriately
    - _Requirements: 10.4_

  - [ ] 10.2 Manual verification of context integration
    - Test that local context influences AI recommendations
    - Verify recommendations reference contextual factors
    - _Requirements: 10.4_

  - [ ] 10.3 Add interactive clarification support
    - Implement functionality for users to request additional reasoning
    - Ensure additional explanations maintain language simplicity
    - _Requirements: 4.5_

  - [ ] 10.4 Manual verification of clarification support
    - Test that additional explanations maintain language simplicity
    - Verify clarification requests work as expected
    - _Requirements: 4.5_

- [ ] 11. Final checkpoint - Complete system integration
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Manual testing with sample CSV files and demo scenarios
- Focus on simple, working implementation over complex features
- Basic logging and demo-time observation for performance validation