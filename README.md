# JEDIDIAH Cafe Wi-Fi Timer Website (browser-based starter)

This is a browser website project designed to be hosted online. The laptop does not need to run Python after the website is hosted; customers/admin open it in Chrome.

## What works
- Admin login
- Add a customer timer
- Countdown timer
- Add 15 minutes
- Stop a timer
- Website dashboard layout for laptop and phone
- Guest information page at `/customer`

## Important limitation
This starter only tracks time in the website. It DOES NOT actually block internet or disconnect a customer's phone when time expires. A hosted website cannot control devices connected to a separate Windows Mobile Hotspot by itself. Real auto-disconnect requires a compatible router/hotspot controller and an integration with it.

## Deploy online (no install on the laptop)
1. Create a GitHub account and a new repository.
2. Upload all files in this folder to the repository.
3. Create an account at Render.com and choose **New + > Blueprint**.
4. Connect your GitHub repository. Render reads `render.yaml`.
5. When asked for `ADMIN_PASSWORD`, set a strong password. Keep username `admin` or change `ADMIN_USER`.
6. Deploy. Open the public website URL Render gives you.
7. Use that URL to open the admin dashboard. The guest page is the same URL plus `/customer`.

## Notes
- The default username is `admin`.
- Set a strong `ADMIN_PASSWORD` in the hosting dashboard before deployment.
- The free web service may sleep when unused, and its local database may not be persistent. For a real business system, use persistent storage/database and a paid always-on host.
- This is a starter project, not a finished Wi-Fi access controller.
