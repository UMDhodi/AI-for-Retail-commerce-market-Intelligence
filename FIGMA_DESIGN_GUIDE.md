# BharatSignal Figma Design Guide

## 🎨 How to Create This Design in Figma

This guide provides step-by-step instructions to recreate the BharatSignal UI in Figma.

---

## 📐 Figma Setup

### 1. Create New Figma File
- File name: "BharatSignal UI Design"
- Canvas size: 1440px width (desktop)
- Add mobile frame: 375px width

### 2. Set Up Design System

#### Create Color Styles
```
Primary/Orange: #FF9933
Primary/Green: #138808
Primary/Blue: #007BFF
Success/Green: #28A745
Warning/Yellow: #FFC107
Danger/Red: #DC3545

Neutral/Background: #F8F9FA
Neutral/White: #FFFFFF
Neutral/Text-Primary: #333333
Neutral/Text-Secondary: #666666
Neutral/Border: #E9ECEF
```

**In Figma**:
1. Create rectangles for each color
2. Right-click → "Create Color Style"
3. Name them as shown above

#### Create Text Styles
```
H1/Bold: Segoe UI, 40px, Bold, #333333
H2/Bold: Segoe UI, 28px, Bold, #2C3E50
H3/Bold: Segoe UI, 20px, Bold, #2C3E50
Body/Regular: Segoe UI, 16px, Regular, #333333
Body/Small: Segoe UI, 14px, Regular, #666666
Button/Bold: Segoe UI, 18px, Bold, #FFFFFF
```

**In Figma**:
1. Create text layers with these properties
2. Right-click → "Create Text Style"
3. Name them as shown above

#### Create Effect Styles
```
Shadow/Card: 
  - X: 0, Y: 4, Blur: 20, Spread: 0
  - Color: #000000, Opacity: 10%

Shadow/Button-Hover:
  - X: 0, Y: 4, Blur: 15, Spread: 0
  - Color: #000000, Opacity: 20%

Shadow/Decision-Card:
  - X: 0, Y: 4, Blur: 12, Spread: 0
  - Color: #28A745, Opacity: 20%
```

---

## 📱 Page 1: Home Page Design

### Frame Setup
1. Create frame: Press `F` → Select "Desktop" → 1440x1024px
2. Name: "Home Page - Desktop"
3. Background: #F8F9FA

### Step-by-Step Components

#### 1. Header (0, 0, 1440, 120)
```
1. Create rectangle: 1440x120px
2. Fill: Linear gradient
   - Start: #FF9933 (left)
   - End: #138808 (right)
   - Angle: 135°
3. Add effect: Drop shadow (0, 2, 10, 0, #000000 10%)
4. Add text: "🇮🇳 BharatSignal"
   - Font: Segoe UI Bold, 40px
   - Color: #FFFFFF
   - Position: Center horizontally, Y: 30
5. Add text: "AI-Powered Business Assistant for Kirana Shops"
   - Font: Segoe UI Regular, 18px
   - Color: #FFFFFF, Opacity: 90%
   - Position: Center horizontally, Y: 75
```

#### 2. Main Container (120, 140, 800, auto)
```
1. Create frame: 800px width, auto height
2. Position: Center horizontally, Y: 140
3. Background: #FFFFFF
4. Corner radius: 12px
5. Padding: 32px
6. Add effect: Shadow/Card
```

#### 3. Intro Section (inside container)
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 0
4. Add text: "Get Smart Business Recommendations"
   - Style: H2/Bold
   - Align: Center
5. Add text: "Upload your sales data and tell us about local events..."
   - Style: Body/Regular
   - Color: #666666
   - Align: Center
```

#### 4. Upload Section
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 24px
4. Background: #FAFBFC
5. Border: 2px solid #E9ECEF
6. Corner radius: 8px
7. Add text: "📊 Upload Your Sales Data"
   - Style: H3/Bold

File Upload Component:
8. Create rectangle: 100% width, 60px height
9. Border: 2px dashed #007BFF
10. Corner radius: 8px
11. Background: #FFFFFF
12. Add text: "Choose CSV file..."
    - Style: Body/Regular
    - Color: #666666
    - Position: Left, centered vertically
13. Add button: "Browse"
    - Size: 80x40px
    - Background: #007BFF
    - Corner radius: 4px
    - Text: "Browse" (white, 14px)
    - Position: Right, centered vertically

File Info Box:
14. Create auto-layout frame
15. Background: #E3F2FD
16. Padding: 16px
17. Border-left: 4px solid #2196F3
18. Corner radius: 6px
19. Add text: "CSV Format Required: date, item, quantity, price"
    - Style: Body/Small
20. Add text: "Example: 2024-01-15, Rice 1kg, 10, 45.00"
    - Style: Body/Small
```

#### 5. Context Input Section
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 24px
4. Background: #FAFBFC
5. Border: 2px solid #E9ECEF
6. Corner radius: 8px
7. Add text: "🤖 Ask AI about your shop"
   - Style: H3/Bold

Textarea:
8. Create rectangle: 100% width, 150px height
9. Border: 2px solid #DDDDDD
10. Corner radius: 8px
11. Background: #FFFFFF
12. Add text (placeholder): "Ask any question about your business:..."
    - Style: Body/Regular
    - Color: #999999
    - Position: Top-left, padding 16px
```

#### 6. Generate Button
```
1. Create rectangle: 100% width, 60px height
2. Fill: Linear gradient
   - Start: #28A745 (top-left)
   - End: #20C997 (bottom-right)
3. Corner radius: 8px
4. Add text: "🤖 Generate AI Recommendations"
   - Style: Button/Bold
   - Color: #FFFFFF
   - Position: Center
5. Add hover state:
   - Duplicate component
   - Add effect: Shadow/Button-Hover
   - Transform: Y: -2px
```

#### 7. Demo Section
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 24px
4. Background: #FFF3CD
5. Border: 1px solid #FFEAA7
6. Corner radius: 8px
7. Add text: "🎯 Try Demo Mode"
   - Style: H3/Bold

Dropdown:
8. Create rectangle: 100% width, 48px height
9. Background: #FFFFFF
10. Border: 2px solid #DDDDDD
11. Corner radius: 6px
12. Add text: "Select a scenario..."
    - Style: Body/Regular
    - Position: Left, padding 16px
13. Add icon: "▼" (dropdown arrow)
    - Position: Right, padding 16px

Buttons:
14. Create two buttons side by side
15. Button 1: "📊 Load Demo Scenario"
    - Background: #6C757D
    - Size: 48% width, 48px height
16. Button 2: "📥 Download Sample CSV"
    - Background: #6C757D
    - Size: 48% width, 48px height
```

#### 8. Help Section
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 24px
4. Background: #FAFBFC
5. Border: 2px solid #E9ECEF
6. Corner radius: 8px
7. Add text: "❓ How It Works"
   - Style: H3/Bold

Steps (horizontal layout):
8. Create 3 step cards in a row
9. Each card:
   - Size: 30% width, auto height
   - Background: #FFFFFF
   - Border: 1px solid #E9ECEF
   - Corner radius: 8px
   - Padding: 16px

Step Card Structure:
10. Circle badge:
    - Size: 40x40px
    - Background: #007BFF
    - Text: "1", "2", "3" (white, bold, 16px)
11. Text: "Upload CSV", "Add Context", "Get AI Recommendations"
    - Style: Body/Regular
    - Position: Below circle
```

#### 9. Footer (0, bottom, 1440, 60)
```
1. Create rectangle: 1440x60px
2. Background: #2C3E50
3. Position: Bottom of page
4. Add text: "© 2024 BharatSignal - Made for Indian Shops"
   - Style: Body/Small
   - Color: #FFFFFF
   - Position: Center
```

---

## 📱 Page 2: Results Page Design

### Frame Setup
1. Create frame: Press `F` → Select "Desktop" → 1440x1800px
2. Name: "Results Page - Desktop"
3. Background: #F8F9FA

### Step-by-Step Components

#### 1. Header (same as home page)
Copy from home page design

#### 2. Back Button (120, 140, 200, 48)
```
1. Create rectangle: 200x48px
2. Background: #007BFF
3. Corner radius: 8px
4. Add text: "← Analyze New Data"
   - Style: Button/Bold
   - Color: #FFFFFF
   - Position: Center
```

#### 3. Results Header (120, 200, 800, auto)
```
1. Create auto-layout frame (vertical)
2. Spacing: 8px
3. Align: Center
4. Add text: "🎯 Your AI Recommendations"
   - Style: H2/Bold
5. Add text: "Based on analysis of 45 sales records"
   - Style: Body/Regular
   - Color: #666666
```

#### 4. Question Context Header (120, 280, 800, auto)
```
1. Create auto-layout frame (vertical)
2. Spacing: 8px
3. Padding: 16px
4. Background: #E3F2FD
5. Border-left: 4px solid #2196F3
6. Corner radius: 8px
7. Add text: "Answer to:"
   - Style: Body/Small
   - Color: #1976D2
   - Font weight: Bold
8. Add text: "Should I restock oil today?"
   - Style: Body/Regular
   - Font style: Italic
   - Color: #333333
```

#### 5. Primary Decision Card (120, 340, 800, auto)
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 32px
4. Background: Linear gradient
   - Start: #F8FFF9 (top-left)
   - End: #F0F8F0 (bottom-right)
5. Border-left: 4px solid #28A745
6. Corner radius: 12px
7. Add effect: Shadow/Card

Card Header:
8. Add text: "🎯 PRIMARY DECISION"
   - Style: H3/Bold
   - Color: #2C3E50

Decision Line (MOST IMPORTANT):
9. Create auto-layout frame
10. Padding: 16px
11. Background: Linear gradient
    - Start: #D4EDDA (top-left)
    - End: #C3E6CB (bottom-right)
12. Border: 2px solid #28A745
13. Corner radius: 8px
14. Add effect: Shadow/Decision-Card
15. Position: Relative
16. Add circle badge (absolute position):
    - Size: 32x32px
    - Background: #28A745
    - Position: Top-left (-8px, -8px)
    - Text: "🎯" (white, 20px)
    - Add shadow
17. Add text: "Decision: YES - RESTOCK OIL NOW"
    - Font: Segoe UI Black, 18px
    - Color: #155724
    - Letter spacing: 0.5px
    - Text shadow: 0 1px 2px rgba(0,0,0,0.1)

Sales Summary:
18. Add text: "Recent Sales Summary:"
    - Style: Body/Regular
    - Font weight: Bold
19. Add bullet list (auto-layout vertical):
    - "Oil 1L: 15 units sold over 7 days"
    - "Average daily sales: 2.1 units"
    - "Sales trending upward (+15%)"
    - Style: Body/Regular
    - Color: #555555

Action:
20. Add text: "Action: Increase oil stock by 20%"
    - Style: Body/Regular

Why:
21. Add text: "Why: Oil sales are growing steadily..."
    - Style: Body/Regular

Confidence:
22. Add text: "Confidence: High (7 days of data)"
    - Style: Body/Regular
    - Color: #28A745
    - Font weight: Bold

Based On:
23. Add text: "Based on: Recent sales data, seasonal patterns..."
    - Style: Body/Regular
```

#### 6. Supporting Signals Card (120, +20, 800, auto)
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 32px
4. Background: Linear gradient
   - Start: #F8F9FF (top-left)
   - End: #F0F4FF (bottom-right)
5. Border-left: 4px solid #007BFF
6. Corner radius: 12px
7. Add effect: Shadow/Card
8. Add text: "📊 SUPPORTING SIGNALS"
   - Style: H3/Bold
9. Add bullet list:
   - "Oil sales increased 15% this week"
   - "Festival season approaching"
   - "Consistent daily demand"
   - Style: Body/Regular
   - Color: #555555
```

#### 7. Risk & Safety Card (120, +20, 800, auto)
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 32px
4. Background: Linear gradient
   - Start: #FFFEF8 (top-left)
   - End: #FFF8E1 (bottom-right)
5. Border-left: 4px solid #FFC107
6. Corner radius: 12px
7. Add effect: Shadow/Card
8. Add text: "⚠️ RISK & SAFETY CHECK"
   - Style: H3/Bold
9. Add bullet list:
   - "Start with 20% increase maximum"
   - "Monitor sales closely for first week"
   - "Keep supplier flexibility"
   - Style: Body/Regular
   - Color: #555555
```

#### 8. Suggested Questions Block (120, +20, 800, auto)
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 32px
4. Background: #E3F2FD
5. Border: 2px solid #2196F3
6. Corner radius: 12px
7. Add text: "💡 Suggested Questions (Tap to Explore More)"
   - Style: H3/Bold
   - Color: #1976D2

Question Chips (horizontal wrap):
8. Create auto-layout frame (horizontal, wrap)
9. Spacing: 8px
10. For each chip:
    - Create auto-layout frame
    - Padding: 12px 16px
    - Background: #FFFFFF
    - Border: 2px solid #2196F3
    - Corner radius: 20px (pill shape)
    - Text: Question text
    - Style: Body/Small
    - Color: #1976D2
    - Font weight: 500

Chip Hover State:
11. Duplicate chip
12. Background: #2196F3
13. Text color: #FFFFFF
14. Add effect: Shadow/Button-Hover
15. Transform: Y: -2px
```

#### 9. Ask AI Section (120, +20, 800, auto)
```
1. Create auto-layout frame (vertical)
2. Spacing: 16px
3. Padding: 32px
4. Background: #F8F9FA
5. Border: 2px solid #E9ECEF
6. Corner radius: 12px
7. Add text: "Ask AI about your shop"
   - Style: H3/Bold

Input Group (horizontal):
8. Create auto-layout frame (horizontal)
9. Spacing: 16px
10. Textarea:
    - Width: 70%
    - Height: 60px
    - Background: #FFFFFF
    - Border: 2px solid #DDDDDD
    - Corner radius: 8px
    - Padding: 16px
11. Button:
    - Width: 28%
    - Height: 60px
    - Background: Linear gradient (#007BFF to #0056B3)
    - Corner radius: 8px
    - Text: "Ask AI"
    - Style: Button/Bold
    - Color: #FFFFFF
```

#### 10. Action Buttons (120, +20, 800, 48)
```
1. Create auto-layout frame (horizontal)
2. Spacing: 16px
3. Button 1: "🖨️ Print Recommendations"
   - Width: 48%
   - Height: 48px
   - Background: #28A745
4. Button 2: "🔄 Try Another Scenario"
   - Width: 48%
   - Height: 48px
   - Background: #FD7E14
```

---

## 📱 Mobile Design (375px width)

### Adaptations

1. **Create Mobile Frame**:
   - Press `F` → Select "iPhone 14 Pro" → 393x852px
   - Name: "Home Page - Mobile"

2. **Adjust Layouts**:
   - Change all horizontal layouts to vertical
   - Full-width components (100%)
   - Reduce padding: 16px instead of 32px
   - Smaller text sizes: -2px from desktop

3. **Touch Targets**:
   - Minimum button height: 44px
   - Minimum chip height: 44px
   - Increase spacing between interactive elements

4. **Responsive Cards**:
   - Stack all cards vertically
   - Full-width question chips
   - Vertical input group (textarea above button)

---

## 🎨 Component Library

### Create Components (Ctrl/Cmd + Alt + K)

1. **Button/Primary**
   - Green gradient background
   - Variants: Default, Hover, Disabled

2. **Button/Secondary**
   - Gray background
   - Variants: Default, Hover, Disabled

3. **Card/Default**
   - White background, shadow
   - Variants: Default, Primary, Info, Warning

4. **Input/Text**
   - White background, border
   - Variants: Default, Focus, Error

5. **Chip/Question**
   - Pill shape, blue border
   - Variants: Default, Hover, Active

---

## 🔄 Prototyping

### Add Interactions

1. **Home Page → Results Page**:
   - Select "Generate AI Recommendations" button
   - Click "+" in Prototype panel
   - Connect to Results Page
   - Transition: Smart Animate, 300ms

2. **Results Page → Home Page**:
   - Select "Analyze New Data" button
   - Connect to Home Page
   - Transition: Dissolve, 300ms

3. **Question Chips**:
   - Select chip
   - On Click → Change to Hover variant
   - After delay (100ms) → Trigger Ask AI flow

4. **Ask AI Button**:
   - On Click → Show loading state
   - After delay (2000ms) → Update decision card

---

## 📤 Export Settings

### For Development

1. **Export Assets**:
   - Select all icons/images
   - Right panel → Export
   - Format: SVG
   - Scale: 1x, 2x, 3x

2. **Export Specs**:
   - Select frame
   - Right-click → "Copy as CSS"
   - Paste into CSS file

3. **Export Colors**:
   - Plugins → "Export Styles to CSS Variables"
   - Copy CSS variables

---

## 🎯 Figma Plugins to Use

1. **Iconify** - For additional icons
2. **Unsplash** - For placeholder images
3. **Content Reel** - For realistic text content
4. **Stark** - For accessibility checking
5. **Autoflow** - For user flow diagrams

---

## 📋 Checklist

- [ ] Set up color styles
- [ ] Set up text styles
- [ ] Set up effect styles
- [ ] Create home page desktop
- [ ] Create results page desktop
- [ ] Create mobile versions
- [ ] Create component library
- [ ] Add prototyping interactions
- [ ] Test accessibility (contrast)
- [ ] Export assets
- [ ] Share with team

---

## 🔗 Resources

- **Figma Community**: Search for "Dashboard UI Kit" for inspiration
- **Indian Design**: Look for "Indian E-commerce" templates
- **Color Gradients**: Use Figma's gradient tool with 135° angle
- **Shadows**: Use multiple shadows for depth

---

## 💡 Pro Tips

1. **Use Auto Layout**: Makes responsive design easier
2. **Create Variants**: For button states and card types
3. **Use Constraints**: For responsive behavior
4. **Name Layers**: Use clear, consistent naming
5. **Organize**: Use frames and groups logically
6. **Version Control**: Save versions before major changes

---

**This guide provides everything you need to recreate the BharatSignal UI in Figma!**

Start with the design system (colors, text styles, effects), then build components, and finally assemble the pages.
