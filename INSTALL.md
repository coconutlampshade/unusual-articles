# WikiWriter Installation Guide

## Step 1: Install Python
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Run the installer you downloaded
   - **IMPORTANT**: Check "Add Python to PATH" box during installation!
   - Click "Install Now"

## Step 2: Download WikiWriter
1. Go to https://github.com/coconutlampshade/wikiwriter
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the file somewhere on your computer
   - Right-click the ZIP file
   - Select "Extract All..."
   - Choose a location you can find easily

## Step 3: Get Your Google API Key
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account if needed
3. Click "Create API Key"
4. Copy the key (you'll need it in Step 4)

## Step 4: Set Up WikiWriter
1. Open the folder where you unzipped WikiWriter
2. Create a new file called `.env`
   - On Windows: Create a new text file and name it exactly `.env`
   - On Mac: Open TextEdit, create new file, save as `.env`
3. Put your API key in the .env file like this:   ```
   GOOGLE_API_KEY=your-key-here   ```
   - Replace "your-key-here" with the key you copied
   - Save the file

## Step 5: Install Requirements
1. Open Terminal/Command Prompt
   - Windows: Press Windows+R, type "cmd", press Enter
   - Mac: Press Command+Space, type "terminal", press Enter
2. Navigate to WikiWriter folder:   ```
   cd path/to/wikiwriter   ```
   (Replace "path/to/wikiwriter" with actual path)
3. Install required packages:   ```
   pip install flask google-generativeai python-dotenv beautifulsoup4 requests   ```

## Step 6: Run WikiWriter
1. In the same Terminal/Command Prompt:   ```
   python app.py   ```
2. Open your web browser
3. Go to: http://localhost:5000

## Common Problems

### "Python not found"
- Make sure you checked "Add Python to PATH" during installation
- Try restarting your computer

### "Module not found"
- Make sure you're in the right folder
- Try running the pip install command again

### "No API key found"
- Check your .env file exists
- Make sure the API key is copied correctly

Need help? Create an issue on GitHub!