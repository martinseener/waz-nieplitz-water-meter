# Installing from GitHub Repository

Complete guide for publishing the add-on to GitHub and installing it in Home Assistant.

## Part 1: Publishing to GitHub

### Step 1: Push to GitHub Repository

You've already created the repository at: `git@github.com:martinseener/waz-nieplitz-water-meter.git`

Run the automated push script:

```bash
cd /Users/mseener/Development/local/waz-nieplitz-water-meter
./push_to_github.sh
```

The script will:
1. Initialize git (if needed)
2. Add the GitHub remote
3. Show you what will be committed
4. Ask for confirmation
5. Commit and push everything to GitHub

**Manual alternative:**

```bash
# Initialize git
git init

# Add remote
git remote add origin git@github.com:martinseener/waz-nieplitz-water-meter.git

# Add all files (respects .gitignore)
git add .

# Commit
git commit -m "Initial commit of WAZ Nieplitz Water Meter add-on v1.2.0"

# Push to main branch
git push -u origin main
```

### Step 2: Verify on GitHub

1. Visit https://github.com/martinseener/waz-nieplitz-water-meter
2. You should see all your files
3. The README will display automatically

### Step 3: Configure Repository (Optional but Recommended)

On GitHub:

1. **Add Description:**
   - Click "About" (gear icon on right side)
   - Description: "Home Assistant add-on for WAZ Nieplitz water meter portal integration"
   - Website: Leave blank or add your HA instance URL
   - Topics: `homeassistant`, `homeassistant-addon`, `water-meter`, `energy-dashboard`
   - Click "Save changes"

2. **Create a Release (Recommended):**
   - Go to "Releases" → "Create a new release"
   - Tag: `v1.2.0`
   - Title: `v1.2.0 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

3. **Add Screenshots (Optional):**
   - Create `docs/images/` directory in your local repo
   - Add screenshots:
     - `config.png` - Add-on configuration screen
     - `energy-dashboard.png` - Energy dashboard with water meters
     - `sensor-attributes.png` - Sensor attributes view
   - Update REPOSITORY_README.md image paths
   - Commit and push

## Part 2: Installing in Home Assistant

### Method 1: Add Repository URL (Recommended)

#### On Your Local Home Assistant (http://homeassistant.local:8123)

1. **Navigate to Add-ons:**
   - Settings → Add-ons → Add-on Store

2. **Add Repository:**
   - Click **⋮** (three dots) in top right
   - Select **Repositories**
   - Paste this URL:
     ```
     https://github.com/martinseener/waz-nieplitz-water-meter
     ```
   - Click **Add**
   - Close the dialog

3. **Refresh the Store:**
   - You might need to refresh the page or wait a moment
   - The store will reload automatically

4. **Find the Add-on:**
   - Scroll down or search for "WAZ Nieplitz"
   - You should see **WAZ Nieplitz Water Meter** with version 1.2.0
   - It will have a "Custom Repository" badge

5. **Install:**
   - Click on the add-on
   - Click **Install**
   - Wait for installation (1-2 minutes for build)

6. **Configure:**
   - Go to **Configuration** tab
   - Enter your credentials:
     ```yaml
     username: your_waz_portal_username
     password: your_waz_portal_password
     update_interval: 2592000
     main_meter_name: Water Meter Main
     garden_meter_name: Water Meter Garden
     ```
   - Click **Save**

7. **Start:**
   - Go to **Info** tab
   - Enable "Start on boot"
   - Enable "Watchdog"
   - Click **Start**

8. **Verify:**
   - Check **Log** tab for successful messages
   - Go to Developer Tools → States
   - Search for `waz_nieplitz`
   - You should see your sensors!

### Method 2: Manual Clone and Install

If you want a local copy:

```bash
# On your Mac, clone to HA's addon directory
# (Requires Samba or SSH access to HA)

# Via Samba:
git clone https://github.com/martinseener/waz-nieplitz-water-meter.git \
  /Volumes/addons/waz-nieplitz-water-meter

# Via SSH to HA:
ssh root@homeassistant.local
cd /addons
git clone https://github.com/martinseener/waz-nieplitz-water-meter.git
exit
```

Then in Home Assistant:
- Settings → Add-ons → ⋮ → Check for updates
- Install as usual

## Part 3: Updating the Add-on

### When You Make Changes

1. **Make changes locally** to your add-on code

2. **Test the changes:**
   ```bash
   ./run_tests.sh
   ```

3. **Update version** in `config.json`:
   ```json
   {
     "version": "1.2.1",
     ...
   }
   ```

4. **Update CHANGELOG.md**

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

6. **Create a release on GitHub** (recommended)

7. **Update in Home Assistant:**
   - Go to the add-on
   - Click "Check for update" (may take a few minutes to appear)
   - Click "Update"

### For Users to Update

Users who installed from your repository:
1. Will see update notifications in Home Assistant
2. Can click "Update" to get the latest version
3. HA automatically pulls from GitHub

## Troubleshooting

### Repository Not Appearing in HA

**Check:**
- URL is exactly: `https://github.com/martinseener/waz-nieplitz-water-meter`
- Repository is public (not private)
- Files are committed to the main/master branch
- `repository.json` exists in the repository root

**Try:**
- Wait 5 minutes and refresh
- Remove and re-add the repository
- Check HA logs: Settings → System → Logs

### Add-on Not Showing After Adding Repository

**Verify:**
1. Repository was added successfully
2. Files are in the correct location in GitHub
3. `config.json` is valid JSON
4. The repository is public

**Check on GitHub:**
- Visit https://github.com/martinseener/waz-nieplitz-water-meter
- Ensure `config.json` is visible
- Click on it and verify it's valid JSON

### "Failed to fetch repository"

**Solutions:**
- Check your internet connection
- Verify the repository URL is correct
- Make sure repository is public
- Try removing and re-adding

### Changes Not Appearing After Update

**Steps:**
1. Verify you pushed to GitHub: Check the repo webpage
2. Update version number in `config.json`
3. Create a new release (tag) on GitHub
4. Wait a few minutes for HA to fetch updates
5. Force refresh: Remove and re-add repository

## Benefits of GitHub Installation

✅ **Easy Updates** - Users get automatic update notifications
✅ **Version Control** - Track all changes with git
✅ **Collaboration** - Others can contribute via Pull Requests
✅ **Distribution** - Easy to share with other WAZ Nieplitz customers
✅ **Backup** - Your code is safely stored on GitHub
✅ **Issues** - Users can report bugs via GitHub Issues
✅ **Professional** - Standard way to distribute HA add-ons

## Sharing with Others

Once published on GitHub, you can share the installation instructions:

```
Add this repository to Home Assistant:
https://github.com/martinseener/waz-nieplitz-water-meter

Then install the "WAZ Nieplitz Water Meter" add-on.
```

## Repository Structure on GitHub

After pushing, your repository will have:

```
martinseener/waz-nieplitz-water-meter/
├── config.json                   - Add-on metadata
├── repository.json               - HA repository info
├── run.py                        - Main add-on code
├── Dockerfile                    - Container definition
├── build.yaml                    - Build configuration
├── requirements.txt              - Python dependencies
├── LICENSE                       - MIT License
├── REPOSITORY_README.md          - Main repository README
├── README.md                     - Add-on documentation
├── CHANGELOG.md                  - Version history
├── INSTALLATION.md               - Installation guide
├── MANUAL_FETCH_SETUP.md         - Manual fetch guide
├── HISTORICAL_READINGS.md        - Historical data guide
├── TESTING.md                    - Testing guide
├── test_addon.py                 - Test suite
├── run_tests.sh                  - Test runner
├── .gitignore                    - Git ignore rules
└── (other documentation files)
```

## Next Steps

1. ✅ Push to GitHub (use `./push_to_github.sh`)
2. ✅ Add repository to Home Assistant
3. ✅ Install and test the add-on
4. ✅ Create a GitHub release for v1.2.0
5. ✅ Add screenshots (optional)
6. ✅ Share with other WAZ Nieplitz customers!

## Support

- **GitHub Issues**: https://github.com/martinseener/waz-nieplitz-water-meter/issues
- **Documentation**: See all .md files in the repository
- **Testing**: Run `./run_tests.sh` before publishing changes
