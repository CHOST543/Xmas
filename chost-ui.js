/* CHOST dashboard add-on
   1) Sidebar: Dashboard, Users, API Keys, Templates, Bulk Actions, Settings, plus three CHOST pages.
      Everything else (Nodes, Hosts, Cores, Admins, Groups, Roles, Statistics...) is hidden for everyone.
   2) Sidebar page "Reseller panel" (owner only): create and manage reseller panels with a data quota.
   3) Sidebar page "Telegram bot" (owner only): bot token, admin IDs, live status and sales numbers.
   4) Sidebar page "Account security": change the password; the owner can also create a 5-minute owner key.
   5) Login page "Owner access": reset the owner login with a CHOST owner key (CH-XXXX-XXXX-XXXX).
   6) Every CHOST text follows the panel language (Persian / English) and text direction, live. */
(function () {
  "use strict";
  var ZWNJ = String.fromCharCode(8204);
  function norm(t) { return String(t || "").split(ZWNJ).join(" ").replace(/[0-9۰-۹]+/g, "").replace(/\s+/g, " ").trim().toLowerCase(); }

  /* ---------- language: follow the panel (Persian or English) ---------- */
  var EN = {"\"><button type=\"button\" tabindex=\"-1\" aria-label=\"نمایش رمز\">": "\"><button type=\"button\" tabindex=\"-1\" aria-label=\"Show password\">", "</div><div class=\"tt\"><b>کلید دسترسی مالک</b><p>یک کلید یک‌بارمصرف با اعتبار 5 دقیقه بسازید. با این کلید در صفحه‌ی ورود و از بخش «دسترسی مالک» می‌توانید نام کاربری و رمز مالک را از نو تنظیم کنید.</p></div>": "</div><div class=\"tt\"><b>Owner access key</b><p>Create a one-time key valid for 5 minutes. On the login page, under \"Owner access\", this key lets you reset the owner username and password.</p></div>", "<span>دریافت کلید</span></button></div>": "<span>Get key</span></button></div>", "<div data-k=\"login\" style=\"display:none\"><div class=\"two\"><div class=\"fld\"><label>نام کاربری مالک</label><input class=\"ltr\" data-k=\"u\" autocomplete=\"username\" spellcheck=\"false\"></div><div class=\"fld\"><label>رمز عبور مالک</label>": "<div data-k=\"login\" style=\"display:none\"><div class=\"two\"><div class=\"fld\"><label>Owner username</label><input class=\"ltr\" data-k=\"u\" autocomplete=\"username\" spellcheck=\"false\"></div><div class=\"fld\"><label>Owner password</label>", "<div class=\"acts\"><button class=\"btn pri\" type=\"button\" data-k=\"ok\">تأیید و دریافت کلید</button></div></div>": "<div class=\"acts\"><button class=\"btn pri\" type=\"button\" data-k=\"ok\">Confirm and get key</button></div></div>", "<span>کپی</span></button></div><div class=\"tm\"><i><b data-k=\"bar\"></b></i><span data-k=\"left\"></span></div></div>": "<span>Copy</span></button></div><div class=\"tm\"><i><b data-k=\"bar\"></b></i><span data-k=\"left\"></span></div></div>", "دریافت کلید ممکن نشد": "Could not get a key", "ارتباط با سرور برقرار نشد": "Could not reach the server", "کلید تازه": "New key", "کلید کپی شد": "Key copied", "اعتبار: ": "Valid for: ", "منقضی شد. یک کلید تازه دریافت کنید.": "Expired. Get a new key.", "</div><div class=\"tt\"><b>تغییر رمز عبور</b><p>رمز عبور حساب خود را تغییر دهید. پس از ذخیره، ورودهای بعدی با رمز جدید انجام می‌شود.</p></div></div>": "</div><div class=\"tt\"><b>Change password</b><p>Change the password of your account. After saving, sign in with the new password.</p></div></div>", "<div class=\"three\"><div class=\"fld\"><label>رمز فعلی</label>": "<div class=\"three\"><div class=\"fld\"><label>Current password</label>", "<div class=\"fld\"><label>رمز جدید</label>": "<div class=\"fld\"><label>New password</label>", "حداقل 4 کاراکتر": "At least 4 characters", "<div class=\"fld\"><label>تکرار رمز جدید</label>": "<div class=\"fld\"><label>Repeat new password</label>", "<div class=\"err\" data-p=\"err\"></div><div class=\"acts\"><button class=\"btn pri\" type=\"button\" data-p=\"save\">ذخیره‌ی رمز عبور</button></div>": "<div class=\"err\" data-p=\"err\"></div><div class=\"acts\"><button class=\"btn pri\" type=\"button\" data-p=\"save\">Save password</button></div>", "ضعیف": "Weak", "متوسط": "Fair", "خوب": "Good", "قوی": "Strong", "رمز فعلی و رمز جدید را وارد کنید": "Enter your current and new password", "رمز جدید باید حداقل 4 کاراکتر باشد": "The new password must be at least 4 characters", "تکرار رمز جدید با رمز جدید یکسان نیست": "The repeated password does not match", "ذخیره ممکن نشد": "Could not save", "رمز عبور با موفقیت تغییر کرد": "Password changed successfully", "\" role=\"dialog\" aria-modal=\"true\"><button class=\"cl\" type=\"button\" aria-label=\"بستن\">": "\" role=\"dialog\" aria-modal=\"true\"><button class=\"cl\" type=\"button\" aria-label=\"Close\">", "انصراف": "Cancel", "پنل نمایندگی": "Reseller panel", "ربات تلگرام": "Telegram bot", "امنیت حساب": "Account security", "<div class=\"card\"><div class=\"empty\"><b>این بخش بارگذاری نشد</b><p>صفحه را یک بار تازه کنید.</p></div></div>": "<div class=\"card\"><div class=\"empty\"><b>This section could not load</b><p>Refresh the page once.</p></div></div>", "فروش خودکار اشتراک در تلگرام؛ کیف پول، خرید فوری، سیستم دعوت با پورسانت، کد تخفیف، اکانت تست، یادآوری تمدید و بکاپ روزانه.": "Automatic subscription sales on Telegram: wallet, instant purchase, referral commissions, discount codes, free trial, renewal reminders and daily backup.", "</div><div class=\"tt\"><b>راه‌اندازی در چهار قدم</b><p>کمتر از دو دقیقه زمان می‌برد.</p></div></div>": "</div><div class=\"tt\"><b>Set up in four steps</b><p>Takes less than two minutes.</p></div></div>", "<li><b>ساخت ربات</b><span>در تلگرام به <span class=\"ltr\">@BotFather</span> پیام دهید، دستور <span class=\"ltr\">/newbot</span> را بفرستید و توکن ربات را کپی کنید.</span></li>": "<li><b>Create the bot</b><span>Message <span class=\"ltr\">@BotFather</span> on Telegram, send <span class=\"ltr\">/newbot</span> and copy the bot token.</span></li>", "<li><b>آیدی عددی مدیر</b><span>آیدی عددی خود را از ربات <span class=\"ltr\">@userinfobot</span> دریافت کنید.</span></li>": "<li><b>Admin numeric ID</b><span>Get your numeric ID from <span class=\"ltr\">@userinfobot</span>.</span></li>", "<li><b>ذخیره در پنل</b><span>توکن و آیدی را در کادر بالا وارد کنید، ربات را فعال کنید و «ذخیره» را بزنید.</span></li>": "<li><b>Save in the panel</b><span>Enter the token and ID in the form above, turn the bot on and press \"Save\".</span></li>", "<li><b>تنظیمات فروش</b><span>ربات را در تلگرام Start کنید و دستور <span class=\"ltr\">/admin</span> را بفرستید تا پلن‌ها، قیمت‌ها و شماره کارت را تنظیم کنید.</span></li></ol>": "<li><b>Sales settings</b><span>Start the bot on Telegram and send <span class=\"ltr\">/admin</span> to set plans, prices and the card number.</span></li></ol>", "رمز عبور حساب خود را تغییر دهید و در صورت نیاز کلید دسترسی مالک بسازید.": "Change your account password and create an owner access key when needed.", "رمز عبور حساب خود را تغییر دهید.": "Change your account password.", "</h1><p>برای هر نماینده یک پنل جدا با سهمیه‌ی حجم بسازید. نماینده با همین آدرس وارد می‌شود و فقط کاربران خودش را می‌بیند.</p></div>": "</h1><p>Create a separate panel with a data quota for each reseller. Resellers sign in at this same address and only see their own users.</p></div>", "<span>نماینده‌ی جدید</span></button></div>": "<span>New reseller</span></button></div>", "<div class=\"card stat\"><div class=\"t\"><span>نماینده‌ها</span>": "<div class=\"card stat\"><div class=\"t\"><span>Resellers</span>", "<div class=\"card stat\"><div class=\"t\"><span>فعال</span>": "<div class=\"card stat\"><div class=\"t\"><span>Active</span>", "<div class=\"card stat\"><div class=\"t\"><span>کل سهمیه</span>": "<div class=\"card stat\"><div class=\"t\"><span>Total quota</span>", "<div class=\"card stat\"><div class=\"t\"><span>کل مصرف</span>": "<div class=\"card stat\"><div class=\"t\"><span>Total usage</span>", "<input type=\"search\" placeholder=\"جست‌وجوی نماینده\" data-a=\"q\"></div><div style=\"flex:1\"></div><button class=\"btn ic\" type=\"button\" title=\"به‌روزرسانی\" data-a=\"ref\">": "<input type=\"search\" placeholder=\"Search resellers\" data-a=\"q\"></div><div style=\"flex:1\"></div><button class=\"btn ic\" type=\"button\" title=\"Refresh\" data-a=\"ref\">", "</div><b>هنوز نماینده‌ای ندارید</b><p>اولین پنل نمایندگی را بسازید و اطلاعات ورود را برای نماینده بفرستید.</p><button class=\"btn pri\" type=\"button\" data-a=\"new2\">": "</div><b>No resellers yet</b><p>Create your first reseller panel and send the login details to the reseller.</p><button class=\"btn pri\" type=\"button\" data-a=\"new2\">", "<div class=\"empty\"><b>نتیجه‌ای پیدا نشد</b><p>نام دیگری را جست‌وجو کنید.</p></div>": "<div class=\"empty\"><b>No results</b><p>Try another name.</p></div>", "غیرفعال": "Disabled", "فعال": "Active", "<button class=\"btn ic sm\" type=\"button\" data-m=\"1\" aria-label=\"عملیات\">": "<button class=\"btn ic sm\" type=\"button\" data-m=\"1\" aria-label=\"Actions\">", "<div class=\"tw\"><table><thead><tr><th>نام کاربری</th><th>وضعیت</th><th>مصرف / سهمیه</th><th>کاربران</th><th style=\"width:56px\"></th></tr></thead><tbody>": "<div class=\"tw\"><table><thead><tr><th>Username</th><th>Status</th><th>Usage / quota</th><th>Users</th><th style=\"width:56px\"></th></tr></thead><tbody>", "<div class=\"empty\"><b>بارگذاری نشد</b><p>": "<div class=\"empty\"><b>Could not load</b><p>", "دوباره امتحان کنید": "Please try again", "فهرست به‌روزرسانی شد": "List refreshed", "<div class=\"empty\"><b>ارتباط با سرور برقرار نشد</b><p>اتصال اینترنت را بررسی کنید و دوباره امتحان کنید.</p></div>": "<div class=\"empty\"><b>Could not reach the server</b><p>Check your internet connection and try again.</p></div>", "پنل نمایندگی CHOST\nآدرس: ": "CHOST reseller panel\nAddress: ", "/dashboard/\nنام کاربری: ": "/dashboard/\nUsername: ", "\nرمز عبور: ": "\nPassword: ", "\nسهمیه: ": "\nQuota: ", "نامحدود": "Unlimited", "نماینده‌ی جدید": "New reseller", "یک پنل نمایندگی با سهمیه‌ی حجم بسازید. نماینده فقط با قالب‌های آماده کاربر می‌سازد.": "Create a reseller panel with a data quota. Resellers can only create users from the ready-made templates.", "ساخت پنل نمایندگی": "Create reseller panel", "<div class=\"fld\"><label>نام کاربری</label><input class=\"ltr\" data-f=\"u\" autocomplete=\"off\" spellcheck=\"false\" placeholder=\"reseller1\"><div class=\"hint\">حروف انگلیسی، عدد و _ (3 تا 32 کاراکتر)</div></div>": "<div class=\"fld\"><label>Username</label><input class=\"ltr\" data-f=\"u\" autocomplete=\"off\" spellcheck=\"false\" placeholder=\"reseller1\"><div class=\"hint\">English letters, digits and _ (3 to 32 characters)</div></div>", "<div class=\"fld\"><label>رمز عبور</label><input class=\"ltr\" data-f=\"p\" autocomplete=\"new-password\" spellcheck=\"false\" placeholder=\"حداقل 4 کاراکتر\"></div>": "<div class=\"fld\"><label>Password</label><input class=\"ltr\" data-f=\"p\" autocomplete=\"new-password\" spellcheck=\"false\" placeholder=\"At least 4 characters\"></div>", "<div class=\"fld\" style=\"margin:0\"><label>سهمیه‌ی حجم (گیگابایت)</label><input class=\"ltr\" data-f=\"g\" type=\"number\" inputmode=\"decimal\" min=\"0\" step=\"any\" value=\"50\"><div class=\"hint\">0 یعنی نامحدود. وقتی سهمیه تمام شود، کاربران نماینده خودکار متوقف می‌شوند.</div></div>": "<div class=\"fld\" style=\"margin:0\"><label>Data quota (GB)</label><input class=\"ltr\" data-f=\"g\" type=\"number\" inputmode=\"decimal\" min=\"0\" step=\"any\" value=\"50\"><div class=\"hint\">0 means unlimited. When the quota runs out, the reseller's users are paused automatically.</div></div>", "نام کاربری باید فقط شامل حروف انگلیسی، عدد و _ و بین 3 تا 32 کاراکتر باشد": "The username may only contain English letters, digits and _ and must be 3 to 32 characters", "رمز عبور باید حداقل 4 کاراکتر باشد": "The password must be at least 4 characters", "سهمیه را درست وارد کنید": "Enter a valid quota", "ساخت ممکن نشد": "Could not create", "پنل نمایندگی ساخته شد": "Reseller panel created", "این اطلاعات را برای نماینده بفرستید. رمز عبور بعداً نمایش داده نمی‌شود.": "Send these details to the reseller. The password will not be shown again.", "<span>کپی اطلاعات ورود</span>": "<span>Copy login details</span>", "بستن": "Close", "اطلاعات ورود کپی شد": "Login details copied", "انجام نشد": "Not done", "افزایش سهمیه": "Add quota", "تنظیم سهمیه": "Set quota", "حجم اضافه برای ": "Extra data for ", "سهمیه‌ی جدید برای ": "New quota for ", " (فعلی: ": " (current: ", " (فعلی: نامحدود)": " (current: unlimited)", "ذخیره": "Save", "حجم اضافه (گیگابایت)": "Extra data (GB)", "سهمیه (گیگابایت)": "Quota (GB)", "مثلاً 50": "e.g. 50", "0 = نامحدود": "0 = unlimited", "<div class=\"hint\">0 یعنی نامحدود.</div>": "<div class=\"hint\">0 means unlimited.</div>", "مقدار را درست وارد کنید": "Enter a valid value", "سهمیه ذخیره شد": "Quota saved", "تغییر رمز عبور": "Change password", "رمز جدید برای ": "New password for ", "<div class=\"fld\" style=\"margin:0\"><label>رمز جدید</label><input class=\"ltr\" data-f=\"p\" autocomplete=\"new-password\" spellcheck=\"false\" placeholder=\"حداقل 4 کاراکتر\"></div>": "<div class=\"fld\" style=\"margin:0\"><label>New password</label><input class=\"ltr\" data-f=\"p\" autocomplete=\"new-password\" spellcheck=\"false\" placeholder=\"At least 4 characters\"></div>", "رمز عبور تغییر کرد": "Password changed", "کپی آدرس پنل": "Copy panel address", "آدرس پنل کپی شد": "Panel address copied", "فعال کردن": "Enable", "نماینده فعال شد": "Reseller enabled", "غیرفعال کردن": "Disable", "نماینده غیرفعال شد": "Reseller disabled", "حذف نماینده": "Delete reseller", "حذف ": "Delete ", "؟": "?", "این نماینده حذف می‌شود و دیگر نمی‌تواند وارد پنل شود. این کار برگشت‌پذیر نیست.": "This reseller will be deleted and can no longer sign in. This cannot be undone.", "حذف": "Delete", "نماینده حذف شد": "Reseller deleted", "دسترسی مالک": "Owner access", "با کلید مالک، نام کاربری و رمز پنل را از نو تنظیم کنید. هر کلید 5 دقیقه اعتبار دارد و فقط یک بار کار می‌کند.": "Reset the panel username and password with the owner key. Each key is valid for 5 minutes and works only once.", "ثبت و ادامه": "Save and continue", "<div class=\"fld\"><label>کلید مالک</label><div class=\"kbox\"><input class=\"ltr\" data-f=\"k\" autocomplete=\"one-time-code\" spellcheck=\"false\" placeholder=\"CH-XXXX-XXXX-XXXX\" maxlength=\"17\"><button class=\"btn sm\" type=\"button\" data-f=\"paste\">": "<div class=\"fld\"><label>Owner key</label><div class=\"kbox\"><input class=\"ltr\" data-f=\"k\" autocomplete=\"one-time-code\" spellcheck=\"false\" placeholder=\"CH-XXXX-XXXX-XXXX\" maxlength=\"17\"><button class=\"btn sm\" type=\"button\" data-f=\"paste\">", "<span>چسباندن</span></button></div></div>": "<span>Paste</span></button></div></div>", "<div class=\"fld\"><label>نام کاربری</label><input class=\"ltr\" data-f=\"u\" autocomplete=\"username\" spellcheck=\"false\" value=\"admin\"></div>": "<div class=\"fld\"><label>Username</label><input class=\"ltr\" data-f=\"u\" autocomplete=\"username\" spellcheck=\"false\" value=\"admin\"></div>", "<div class=\"two\"><div class=\"fld\"><label>رمز جدید</label>": "<div class=\"two\"><div class=\"fld\"><label>New password</label>", "<div class=\"sm\"><i><b data-f=\"bar\"></b></i><span data-f=\"lvl\"></span></div></div><div class=\"fld\"><label>تکرار رمز</label>": "<div class=\"sm\"><i><b data-f=\"bar\"></b></i><span data-f=\"lvl\"></span></div></div><div class=\"fld\"><label>Repeat password</label>", "دوباره وارد کنید": "Enter it again", "<details><summary>کلید مالک را از کجا بگیرم؟</summary><ol><li>اگر وارد پنل هستید: از منو، بخش <b>امنیت حساب</b> و دکمه‌ی «دریافت کلید».</li><li>اگر وارد نمی‌شوید: سرویس را در Railway ری‌استارت کنید و در لاگ‌ها خط <code>OWNER KEY</code> را پیدا کنید.</li></ol></details>": "<details><summary>Where do I get the owner key?</summary><ol><li>If you are signed in: open <b>Account security</b> from the menu and press \"Get key\".</li><li>If you cannot sign in: restart the service on Railway and find the <code>OWNER KEY</code> line in the logs.</li></ol></details>", "کلید مالک کامل نیست. قالب صحیح: CH-XXXX-XXXX-XXXX": "The owner key is incomplete. Correct format: CH-XXXX-XXXX-XXXX", "تکرار رمز با رمز جدید یکسان نیست": "The repeated password does not match", "ثبت ممکن نشد": "Could not save", "ورود به پنل": "Go to sign in", "</div><b>رمز پنل تنظیم شد</b><p>از این به بعد با نام کاربری <b class=\"ltr\" style=\"display:inline;font-size:inherit\"></b> و رمز جدید وارد شوید.</p></div>": "</div><b>Panel password set</b><p>From now on, sign in with the username <b class=\"ltr\" style=\"display:inline;font-size:inherit\"></b> and your new password.</p></div>", "<a role=\"button\" tabindex=\"0\" style=\"cursor:pointer;color:var(--ch-mf);text-decoration:underline;text-underline-offset:4px\">دسترسی مالک</a>": "<a role=\"button\" tabindex=\"0\" style=\"cursor:pointer;color:var(--ch-mf);text-decoration:underline;text-underline-offset:4px\">Owner access</a>", "</div><div class=\"tt\"><b>ربات فروش تلگرام</b><p>کاربر پلن را انتخاب می‌کند، مبلغ را کارت‌به‌کارت می‌کند و رسید را می‌فرستد. پس از تأیید شما، اشتراک به‌صورت خودکار ساخته و برای کاربر ارسال می‌شود.</p></div><span class=\"pill off\" data-b=\"pill\"><i></i><span>خاموش</span></span></div>": "</div><div class=\"tt\"><b>Telegram sales bot</b><p>Customers pick a plan, pay by card transfer and send the receipt. After you approve it, the subscription is created and sent to them automatically.</p></div><span class=\"pill off\" data-b=\"pill\"><i></i><span>Off</span></span></div>", "<div class=\"kp\"><div><span>فروش امروز</span><b data-k=\"sales_today\">0</b></div><div><span>درآمد امروز (تومان)</span><b data-k=\"revenue_today\">0</b></div><div><span>کل فروش</span><b data-k=\"sales\">0</b></div><div><span>رسید در انتظار</span><b data-k=\"pending\">0</b></div></div>": "<div class=\"kp\"><div><span>Sales today</span><b data-k=\"sales_today\">0</b></div><div><span>Revenue today (Toman)</span><b data-k=\"revenue_today\">0</b></div><div><span>Total sales</span><b data-k=\"sales\">0</b></div><div><span>Pending receipts</span><b data-k=\"pending\">0</b></div></div>", "<div class=\"sw\"><div><b>فعال بودن ربات</b><small>در حالت خاموش، ربات به هیچ پیامی پاسخ نمی‌دهد.</small></div><button class=\"tg\" type=\"button\" role=\"switch\" aria-checked=\"false\" data-b=\"en\"></button></div>": "<div class=\"sw\"><div><b>Bot enabled</b><small>When off, the bot does not reply to any message.</small></div><button class=\"tg\" type=\"button\" role=\"switch\" aria-checked=\"false\" data-b=\"en\"></button></div>", "<div class=\"two\"><div class=\"fld\"><label>توکن ربات</label><div class=\"pw\"><input class=\"ltr\" data-b=\"tok\" type=\"password\" autocomplete=\"off\" spellcheck=\"false\" placeholder=\"123456789:AA…\"><button type=\"button\" tabindex=\"-1\" aria-label=\"نمایش\">": "<div class=\"two\"><div class=\"fld\"><label>Bot token</label><div class=\"pw\"><input class=\"ltr\" data-b=\"tok\" type=\"password\" autocomplete=\"off\" spellcheck=\"false\" placeholder=\"123456789:AA…\"><button type=\"button\" tabindex=\"-1\" aria-label=\"Show\">", "</button></div><div class=\"hint\">از ربات <span class=\"ltr\">@BotFather</span> دریافت کنید.</div></div>": "</button></div><div class=\"hint\">Get it from <span class=\"ltr\">@BotFather</span>.</div></div>", "<div class=\"fld\"><label>آیدی عددی مدیر</label><input class=\"ltr\" data-b=\"adm\" inputmode=\"numeric\" autocomplete=\"off\" spellcheck=\"false\" placeholder=\"123456789\"><div class=\"hint\">از ربات <span class=\"ltr\">@userinfobot</span> دریافت کنید. چند مدیر را با کاما از هم جدا کنید.</div></div></div>": "<div class=\"fld\"><label>Admin numeric ID</label><input class=\"ltr\" data-b=\"adm\" inputmode=\"numeric\" autocomplete=\"off\" spellcheck=\"false\" placeholder=\"123456789\"><div class=\"hint\">Get it from <span class=\"ltr\">@userinfobot</span>. Separate several admins with commas.</div></div></div>", "<div class=\"acts\"><button class=\"btn pri\" type=\"button\" data-b=\"save\">ذخیره</button><button class=\"btn\" type=\"button\" data-b=\"test\">ارسال پیام آزمایشی</button><span class=\"sp\"></span><a class=\"btn\" data-b=\"open\" target=\"_blank\" rel=\"noopener\" style=\"display:none\">": "<div class=\"acts\"><button class=\"btn pri\" type=\"button\" data-b=\"save\">Save</button><button class=\"btn\" type=\"button\" data-b=\"test\">Send test message</button><span class=\"sp\"></span><a class=\"btn\" data-b=\"open\" target=\"_blank\" rel=\"noopener\" style=\"display:none\">", "<span>باز کردن ربات</span></a></div>": "<span>Open bot</span></a></div>", "<div class=\"note\">منوی مدیریت ربات (دستور <span class=\"ltr\">/admin</span>) شامل پلن‌ها و قیمت‌ها، اطلاعات پرداخت، مدیریت کاربران (افزایش و کاهش موجودی، پیام، مسدودسازی)، کیف پول و سیستم دعوت، کدهای تخفیف، اکانت تست رایگان، متن‌ها، کانال و عضویت اجباری، رسیدهای در انتظار، پیام همگانی، بکاپ کامل و باز و بسته کردن فروش است. یادآوری تمدید و بکاپ روزانه به‌صورت خودکار انجام می‌شوند.</div>": "<div class=\"note\">The bot admin menu (<span class=\"ltr\">/admin</span>) covers plans and prices, payment details, user management (add or subtract balance, messages, blocking), wallet and referrals, discount codes, the free trial, texts, channel and forced join, pending receipts, broadcasts, full backup and opening or closing sales. Renewal reminders and the daily backup run automatically.</div>", "آنلاین": "Online", "خطا در اتصال": "Connection error", "در حال اتصال…": "Connecting…", "خاموش": "Off", "ذخیره نشد": "Not saved", "تنظیمات ذخیره شد. ربات چند لحظه‌ی دیگر آنلاین می‌شود": "Settings saved. The bot will be online in a moment", "تنظیمات ذخیره شد. ربات خاموش است": "Settings saved. The bot is off", "ارسال نشد": "Not sent", "پیام آزمایشی برای ": "Test message sent to ", " مدیر ارسال شد": " admin(s)", "<span>عضویت در کانال</span>": "<span>Join the channel</span>", "<b>سازنده‌ی پنل: <span class=\"ltr\" style=\"letter-spacing:3px\"></span></b><p>این پنل اختصاصی توسط <b class=\"ltr\" style=\"display:inline;font-size:inherit\"></b> ساخته و پشتیبانی می‌شود.<br>برای اطلاع از آپدیت‌ها، آموزش‌ها و پشتیبانی، عضو کانال رسمی شوید.</p>": "<b>Panel creator: <span class=\"ltr\" style=\"letter-spacing:3px\"></span></b><p>This private panel is built and supported by <b class=\"ltr\" style=\"display:inline;font-size:inherit\"></b>.<br>Join the official channel for updates, guides and support.</p>", "تعداد تلاش‌ها زیاد بود. 10 دقیقه‌ی دیگر دوباره امتحان کنید": "Too many attempts. Try again in 10 minutes", "نام کاربری و رمز مالک را وارد کنید": "Enter the owner username and password", "نام کاربری یا رمز عبور اشتباه است": "Wrong username or password", "نشست شما منقضی شده است. دوباره وارد پنل شوید": "Your session has expired. Sign in again", "فقط مالک پنل می‌تواند کلید دریافت کند": "Only the panel owner can get a key", "ساخت کلید انجام نشد": "Could not create a key", "نام کاربری باید فقط شامل حروف انگلیسی، عدد و _ باشد (3 تا 32 کاراکتر)": "The username may only contain English letters, digits and _ (3 to 32 characters)", "کلید اشتباه است یا منقضی شده": "The key is wrong or expired", "ذخیره انجام نشد. یک کلید تازه دریافت کنید و دوباره امتحان کنید": "Could not save. Get a new key and try again", "رمز فعلی اشتباه است": "The current password is wrong", "ذخیره‌ی رمز انجام نشد. دوباره امتحان کنید": "Could not save the password. Try again", "فقط مالک پنل به این بخش دسترسی دارد": "Only the panel owner can access this section", "لیست نماینده‌ها از پنل دریافت نشد": "Could not load the reseller list", "سهمیه را درست وارد کنید (0 یعنی نامحدود)": "Enter a valid quota (0 means unlimited)", "نقش نماینده پیدا نشد. سرویس را یک بار ری‌استارت کنید": "Reseller role not found. Restart the service once", "این نام کاربری قبلاً ثبت شده است": "This username is already taken", "نماینده پیدا نشد": "Reseller not found", "ذخیره‌ی رمز انجام نشد": "Could not save the password", "مقدار حجم را درست وارد کنید": "Enter a valid data amount", "سهمیه‌ی این نماینده نامحدود است": "This reseller has an unlimited quota", "دستور نامعتبر": "Invalid action", "آیدی عددی مدیر باید فقط عدد باشد (چند آیدی را با کاما جدا کنید)": "The admin ID must be numbers only (separate several IDs with commas)", "توکن ربات را وارد کنید": "Enter the bot token", "حداقل یک آیدی عددی مدیر وارد کنید": "Enter at least one admin numeric ID", "توکن معتبر نیست. توکن را از @BotFather کپی کنید": "The token is not valid. Copy it from @BotFather", "ابتدا توکن ربات را ذخیره کنید": "Save the bot token first", "پیام ارسال نشد. ابتدا ربات را در تلگرام Start کنید و دوباره امتحان کنید.": "Message not sent. Start the bot on Telegram first and try again.", "بازگشت": "Back"};
  var EN_PRE = {"تلگرام این توکن را تأیید نکرد: ": "Telegram rejected this token: ", "توکن نامعتبر است یا اتصال به تلگرام برقرار نشد: ": "Invalid token or Telegram is unreachable: ", "اتصال به تلگرام قطع شد، دوباره تلاش می‌کنم: ": "Lost connection to Telegram, retrying: ", "پیام ارسال نشد. ابتدا ربات را در تلگرام Start کنید و دوباره امتحان کنید.": "Message not sent. Start the bot on Telegram first and try again."};
  var EN_RE = [
    [/^کلید اشتباه است یا منقضی شده \((\d+) تلاش باقی‌مانده\)$/, "The key is wrong or expired ($1 attempts left)"],
    [/^ساخت نماینده ممکن نشد \((\d+)\)$/, "Could not create the reseller ($1)"],
    [/^ذخیره ممکن نشد \((\d+)\)$/, "Could not save ($1)"],
    [/^حذف ممکن نشد \((\d+)\)$/, "Could not delete ($1)"]
  ];
  var _lg = { v: null, t: 0, last: null };
  try { _lg.last = sessionStorage.getItem("ch-lang"); } catch (e) {}
  function nativeLang() {   /* the panel's own menu text, never CHOST's own elements */
    var items = document.querySelectorAll('[data-sidebar="menu-button"], [data-sidebar="menu-sub-button"]');
    for (var i = 0; i < items.length; i++) {
      if (items[i].closest && items[i].closest("[data-ch]")) continue;
      var tx = items[i].textContent || "";
      if (/[\u0600-\u06FF]/.test(tx)) return "fa";
      if (/[A-Za-z]{3,}/.test(tx.replace(/\bAPI\b/g, ""))) return "en";
    }
    return null;
  }
  function pageLang() {     /* login page and other screens without a menu */
    var els = document.querySelectorAll("button, label, h1, h2, h3, p, a"), fa = 0, en = 0;
    for (var i = 0; i < els.length && i < 300; i++) {
      if (els[i].closest && els[i].closest(".chx")) continue;
      var tx = els[i].textContent || "";
      if (/[\u0600-\u06FF]/.test(tx)) fa++; else if (/[A-Za-z]{3,}/.test(tx)) en++;
    }
    return fa || en ? (fa >= en ? "fa" : "en") : null;
  }
  function LANG() {
    var now = Date.now(); if (_lg.v && now - _lg.t < 300) return _lg.v;
    var v = nativeLang();
    if (!v) { var l = ""; try { l = String(localStorage.getItem("i18nextLng") || "").toLowerCase(); } catch (e) {}
      if (l) v = l.indexOf("fa") === 0 || l.indexOf("per") === 0 ? "fa" : "en"; }
    if (!v) v = _lg.last || pageLang() || "fa";
    if (v !== _lg.last) { _lg.last = v; try { sessionStorage.setItem("ch-lang", v); } catch (e) {} }
    _lg.v = v; _lg.t = now; return v;
  }
  function DIR() { return LANG() === "fa" ? "rtl" : "ltr"; }
  function T(s) {
    if (s == null || LANG() === "fa") return s;
    s = String(s); if (EN.hasOwnProperty(s)) return EN[s];
    for (var k in EN_PRE) if (s.indexOf(k) === 0) return EN_PRE[k] + s.slice(k.length);
    for (var i = 0; i < EN_RE.length; i++) { var m = s.match(EN_RE[i][0]); if (m) return EN_RE[i][1].replace("$1", m[1]); }
    return s;
  }
  /* ---------- 1) sidebar: whitelist of top-level items + blacklist by link ---------- */
  var KEEP = ["داشبورد", "dashboard", "کاربران", "users", "کلیدهای api", "کلید های api", "api keys",
              "قالب ها", "قالبها", "templates", "عملیات گروهی", "bulk actions", "bulk", "تنظیمات", "settings",
              ].map(norm);   /* "پشتیبانی از ما" (donation) is hidden: the CHOST creator card replaces it */
  var HIDE_TXT = ["نودها", "نود", "nodes", "node", "هاست ها", "هاستها", "میزبان ها", "hosts", "host settings",
                  "هسته ها", "هسته", "پیکربندی هسته", "تنظیمات هسته", "cores", "core", "core settings", "core config",
                  "مدیران", "ادمین ها", "admins", "admin", "گروه ها", "گروهها", "groups", "نقش ها", "roles", "admin roles",
                  "آمار", "statistics", "stats", "usage", "پشتیبانی از ما", "حمایت از ما", "حمایت مالی", "support us", "donate", "sponsor"].map(norm);
  var HIDE_HREF = /\/(nodes?|hosts?|cores?|core-?settings|admins?|admin-roles|roles|groups|statistics|stats|donate|donation|support-us|sponsor)(\/|\?|#|$)/i;
  function sidebars() {
    var s = document.querySelectorAll('[data-sidebar="sidebar"]');
    if (!s.length) s = document.querySelectorAll("aside, nav");
    return Array.prototype.slice.call(s).filter(function (x) { return !(x.closest && x.closest(".chx")) && !(x.parentElement && x.parentElement.closest && x.parentElement.closest('[data-sidebar="sidebar"]')); });
  }
  function label(el) { var t = el.querySelector("span, p") || el; return norm(t.textContent); }
  function hideItem(el) { if (el && el.style.display !== "none") { el.style.display = "none"; el.setAttribute("data-jx", "hidden"); } }
  var KEEP_HREF = /\/(users?|templates?|user-?templates|api-?keys?|bulk[\w-]*|settings)(\/|\?|#|$)|^\/?(dashboard\/?)?(#\/?)?$/i;
  function sweep() {          /* every copy of the menu (desktop and the phone menu behind the three lines) */
    sidebars().forEach(function (side) {
      var links = side.querySelectorAll('a, [data-sidebar="menu-sub-button"], [data-sidebar="menu-button"]');
      for (var j = 0; j < links.length; j++) {
        var a = links[j], href = a.getAttribute("href") || "", txt = label(a);
        if (a.closest && a.closest("[data-ch]")) continue;
        if (href && KEEP_HREF.test(href) && !HIDE_HREF.test(href)) continue;
        if (KEEP.indexOf(txt) > -1) continue;
        if (HIDE_HREF.test(href) || HIDE_TXT.indexOf(txt) > -1) hideItem(a.closest('[data-sidebar="menu-sub-item"], [data-sidebar="menu-item"], li') || a);
      }
    });
  }

  /* ---------- helpers ---------- */
  function findToken() {
    var jwt = /(eyJ[\w-]+\.[\w-]+\.[\w-]+)/, stores = [];
    try { stores.push(localStorage); } catch (e) {}
    try { stores.push(sessionStorage); } catch (e) {}
    for (var s = 0; s < stores.length; s++) for (var i = 0; i < stores[s].length; i++) {
      var m = jwt.exec(String(stores[s].getItem(stores[s].key(i)) || "")); if (m) return m[1];
    }
    var c = jwt.exec(document.cookie || ""); return c ? c[1] : null;
  }
  var OWNER = null, askedFor = null, busy = false;
  function whoAmI() {                       /* once per login token */
    var t = findToken();
    if (!t) { OWNER = null; askedFor = null; return; }
    if (t === askedFor || busy) return;
    busy = true;
    fetch("/api/admin", { headers: { Authorization: "Bearer " + t } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (me) { busy = false; askedFor = t; OWNER = me ? !!(me.role && me.role.is_owner) : null; schedule();
        if (OWNER === true) post("/chost/hello", {}, t).catch(function () {}); })
      .catch(function () { busy = false; setTimeout(schedule, 30000); });
  }
  function fa(n) { return String(n); }
  function post(url, body, token) {
    var hd = { "Content-Type": "application/json" }; if (token) hd.Authorization = "Bearer " + token;
    return fetch(url, { method: "POST", headers: hd, body: JSON.stringify(body || {}), credentials: "same-origin" })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (j && typeof j.detail === "string") j.detail = T(j.detail); if (j && typeof j.error === "string") j.error = T(j.error); return [r.status, j]; }); });
  }
  function heading(words, pathRe) {
    var hs = document.querySelectorAll("main h1, main h2, h1, h2");
    for (var i = 0; i < hs.length; i++) if (words.indexOf(norm(hs[i].textContent)) > -1) return hs[i];
    if (pathRe.test(location.pathname + location.hash)) return document.querySelector("main h1, main h2, h1, h2") || null;
    return null;
  }
  function place(box, h) { var anchor = h.closest("header") || h.parentElement || h; if (!anchor.parentNode) return false; anchor.parentNode.insertBefore(box, anchor.nextSibling); return true; }

  /* ---------- 2) owner key card inside "API Keys" ---------- */
  function bcss() { ucss(); if (!document.getElementById("ch-bot-css")) { var st = document.createElement("style"); st.id = "ch-bot-css"; st.textContent = BCSS + KCSS; document.head.appendChild(st); } }
  var KCSS = ".chb .lg.pr{background:var(--ch-pr);color:var(--ch-pf)}" +
    ".chb .kv{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:4px}.chb .kv code{flex:1 1 220px;min-width:0;max-width:100%;overflow-wrap:anywhere;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:19px;line-height:1.4;font-weight:700;letter-spacing:.12em;direction:ltr;text-align:center;padding:12px 14px;border-radius:var(--ch-r);border:1px dashed var(--ch-bd);background:var(--ch-mu);user-select:all}" +
    ".chb .tm{display:flex;align-items:center;gap:10px;margin-top:12px;font-size:12.5px;line-height:1.5;color:var(--ch-mf)}.chb .tm span{flex:none;white-space:nowrap}.chb .tm i{flex:1;height:4px;border-radius:4px;background:var(--ch-mu);overflow:hidden;display:flex}.chb .tm i b{display:block;height:100%;background:var(--ch-pr);transition:width .5s linear}" +
    ".chb .tm.end i b{background:#e5484d}.chb .three{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:0 12px}" +
    ".chb .sm{font-size:12px;margin-top:6px;display:flex;align-items:center;gap:6px;color:var(--ch-mf)}.chb .sm i{flex:1;height:4px;border-radius:4px;background:var(--ch-mu);overflow:hidden;display:flex}.chb .sm i b{display:block;height:100%;width:0;transition:width .25s,background .25s}";
  var IC_LOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>';
  function pwInput(attr, ph, ac) { return '<div class="pw"><input class="ltr" ' + attr + ' type="password" autocomplete="' + ac + '" spellcheck="false" placeholder="' + ph + T('"><button type="button" tabindex="-1" aria-label="نمایش رمز">') + IC.eye + "</button></div>"; }
  function wireEyes(root) { Array.prototype.forEach.call(root.querySelectorAll(".pw button"), function (b) { b.onclick = function () { var i = b.parentNode.querySelector("input"), show = i.type === "password"; i.type = show ? "text" : "password"; b.innerHTML = show ? IC.eyeoff : IC.eye; }; }); }
  function keyCard(parent) {
    bcss();
    var box = document.createElement("section"); box.id = "jx-owner-key"; box.className = "chx chb"; box.dir = DIR(); themeVars(box);
    box.innerHTML = '<div class="top" style="margin-bottom:14px"><div class="lg pr">' + IC.key + T('</div><div class="tt"><b>کلید دسترسی مالک</b><p>یک کلید یک‌بارمصرف با اعتبار 5 دقیقه بسازید. با این کلید در صفحه‌ی ورود و از بخش «دسترسی مالک» می‌توانید نام کاربری و رمز مالک را از نو تنظیم کنید.</p></div>') +
      '<button class="btn pri" type="button" data-k="get">' + IC.key + T('<span>دریافت کلید</span></button></div>') +
      T('<div data-k="login" style="display:none"><div class="two"><div class="fld"><label>نام کاربری مالک</label><input class="ltr" data-k="u" autocomplete="username" spellcheck="false"></div><div class="fld"><label>رمز عبور مالک</label>') + pwInput('data-k="p"', "", "current-password") + '</div></div>' +
      T('<div class="acts"><button class="btn pri" type="button" data-k="ok">تأیید و دریافت کلید</button></div></div>') +
      '<div data-k="out" style="display:none"><div class="kv"><code data-k="code"></code><button class="btn" type="button" data-k="copy">' + IC.copy + T('<span>کپی</span></button></div><div class="tm"><i><b data-k="bar"></b></i><span data-k="left"></span></div></div>') +
      '<div class="err" data-k="err"></div>';
    parent.appendChild(box);
    wireEyes(box);
    var $k = function (n) { return box.querySelector('[data-k="' + n + '"]'); }, timer, err = $k("err");
    function showErr(m) { err.textContent = m || ""; err.classList.toggle("on", !!m); }
    function request(body, token, btn) {
      showErr(""); btn.disabled = true;
      post("/chost/key", body, token).then(function (x) {
        btn.disabled = false;
        if (x[0] === 200) return show(x[1]);
        if (x[0] === 401 && !body) { $k("login").style.display = ""; $k("u").focus(); return; }
        showErr(x[1].detail || T("دریافت کلید ممکن نشد"));
      }).catch(function () { btn.disabled = false; showErr(T("ارتباط با سرور برقرار نشد")); });
    }
    function show(j) {
      $k("login").style.display = "none"; $k("out").style.display = ""; $k("code").textContent = j.key;
      $k("get").lastChild.textContent = T("کلید تازه");
      var ttl = (j.ttl || 300) * 1000, end = Date.now() + ttl, tm = box.querySelector(".tm");
      $k("copy").onclick = function () { copyText(j.key).then(function () { toast(T("کلید کپی شد")); }); };
      clearInterval(timer);
      (function tickK() {
        var r = Math.max(0, end - Date.now()), s = Math.round(r / 1000);
        $k("bar").style.width = (r / ttl * 100) + "%"; tm.classList.toggle("end", s <= 30);
        $k("left").textContent = s ? T("اعتبار: ") + Math.floor(s / 60) + ":" + ("0" + s % 60).slice(-2) : T("منقضی شد. یک کلید تازه دریافت کنید.");
        if (!s) { clearInterval(timer); $k("code").style.opacity = ".4"; } else $k("code").style.opacity = "";
      })();
      timer = setInterval(function () { if (!document.body.contains(box)) return clearInterval(timer); var r = Math.max(0, end - Date.now()), s = Math.round(r / 1000);
        $k("bar").style.width = (r / ttl * 100) + "%"; tm.classList.toggle("end", s <= 30);
        $k("left").textContent = s ? T("اعتبار: ") + Math.floor(s / 60) + ":" + ("0" + s % 60).slice(-2) : T("منقضی شد. یک کلید تازه دریافت کنید.");
        if (!s) { clearInterval(timer); $k("code").style.opacity = ".4"; } }, 500);
    }
    $k("get").onclick = function () { request(null, findToken(), this); };
    $k("ok").onclick = function () { request({ username: $k("u").value.trim(), password: $k("p").value }, null, this); };
    $k("p").onkeydown = function (e) { if (e.key === "Enter") $k("ok").click(); };
  }

  /* ---------- 3) change password card inside "Settings" (owner and resellers, own account) ---------- */
  function passCard(parent) {
    bcss();
    var box = document.createElement("section"); box.id = "jx-pass"; box.className = "chx chb"; box.dir = DIR(); themeVars(box);
    box.innerHTML = '<div class="top" style="margin-bottom:14px"><div class="lg pr">' + IC_LOCK + T('</div><div class="tt"><b>تغییر رمز عبور</b><p>رمز عبور حساب خود را تغییر دهید. پس از ذخیره، ورودهای بعدی با رمز جدید انجام می‌شود.</p></div></div>') +
      T('<div class="three"><div class="fld"><label>رمز فعلی</label>') + pwInput('data-p="cur"', "", "current-password") + '</div>' +
      T('<div class="fld"><label>رمز جدید</label>') + pwInput('data-p="new"', T("حداقل 4 کاراکتر"), "new-password") + '<div class="sm"><i><b data-p="bar"></b></i><span data-p="lvl"></span></div></div>' +
      T('<div class="fld"><label>تکرار رمز جدید</label>') + pwInput('data-p="rep"', "", "new-password") + '</div></div>' +
      T('<div class="err" data-p="err"></div><div class="acts"><button class="btn pri" type="button" data-p="save">ذخیره‌ی رمز عبور</button></div>');
    parent.appendChild(box);
    wireEyes(box);
    var $p = function (n) { return box.querySelector('[data-p="' + n + '"]'); }, err = $p("err");
    var cols = ["#e5484d", "#f5a524", "#30a46c", "#30a46c"], names = [T("ضعیف"), T("متوسط"), T("خوب"), T("قوی")];
    $p("new").addEventListener("input", function () { var v = this.value, s = strength(v), b = $p("bar"); b.style.width = (v ? Math.max(1, s) * 25 : 0) + "%"; b.style.background = cols[Math.max(0, s - 1)]; $p("lvl").textContent = v ? names[Math.max(0, s - 1)] : ""; });
    function showErr(m) { err.textContent = m || ""; err.classList.toggle("on", !!m); }
    $p("save").onclick = function () {
      var cur = $p("cur").value, nw = $p("new").value, rp = $p("rep").value, btn = this;
      if (!cur || !nw) return showErr(T("رمز فعلی و رمز جدید را وارد کنید"));
      if (nw.length < 4) return showErr(T("رمز جدید باید حداقل 4 کاراکتر باشد"));
      if (nw !== rp) return showErr(T("تکرار رمز جدید با رمز جدید یکسان نیست"));
      btn.disabled = true; showErr("");
      post("/chost/password", { current: cur, new: nw }, findToken()).then(function (x) {
        btn.disabled = false;
        if (x[0] !== 200) return showErr(x[1].detail || T("ذخیره ممکن نشد"));
        $p("cur").value = $p("new").value = $p("rep").value = ""; $p("bar").style.width = "0"; $p("lvl").textContent = "";
        toast(T("رمز عبور با موفقیت تغییر کرد"));
      }).catch(function () { btn.disabled = false; showErr(T("ارتباط با سرور برقرار نشد")); });
    };
    $p("rep").onkeydown = function (e) { if (e.key === "Enter") $p("save").click(); };
  }

  /* ---------- shared: look exactly like the panel (colors, radius, font come from the live theme) ---------- */
  function pick(sel, prop) { var el = document.querySelector(sel); if (!el) return null; var v = getComputedStyle(el)[prop]; return v && v !== "rgba(0, 0, 0, 0)" && v !== "transparent" ? v : null; }
  function themeVars(el) {
    var body = getComputedStyle(document.body), bg = body.backgroundColor, fg = body.color;
    if (!bg || bg === "rgba(0, 0, 0, 0)" || bg === "transparent") bg = getComputedStyle(document.documentElement).backgroundColor;
    if (!bg || bg === "rgba(0, 0, 0, 0)" || bg === "transparent") bg = document.documentElement.classList.contains("dark") ? "#09090b" : "#ffffff";
    var pb = document.querySelector('button[class*="bg-primary"]'), pr = null, pf = null, rad = null;
    if (pb) { var s = getComputedStyle(pb); pr = s.backgroundColor; pf = s.color; rad = s.borderTopLeftRadius; }
    var v = {
      "--ch-bg": bg, "--ch-fg": fg,
      "--ch-card": pick('[class*="bg-card"]', "backgroundColor") || bg,
      "--ch-mf": pick('[class*="text-muted-foreground"]', "color") || "rgba(127,127,127,.95)",
      "--ch-mu": pick('[class*="bg-muted"]', "backgroundColor") || "rgba(127,127,127,.12)",
      "--ch-bd": pick('[class*="border-border"], [class*="border-input"], aside [class*="border"]', "borderTopColor") || "rgba(127,127,127,.25)",
      "--ch-pr": pr && pr !== "rgba(0, 0, 0, 0)" ? pr : fg, "--ch-pf": pf || bg, "--ch-r": rad && rad !== "0px" ? rad : "8px"
    };
    for (var k in v) el.style.setProperty(k, v[k]);
  }
  var UCSS =
    ".chx{font:inherit;font-size:14px;line-height:1.7;color:var(--ch-fg);-webkit-font-smoothing:antialiased;text-align:start;letter-spacing:normal;word-spacing:normal}.chx *{box-sizing:border-box;letter-spacing:normal}.chx p,.chx span,.chx b,.chx label,.chx li,.chx h1,.chx h2{white-space:normal;overflow-wrap:anywhere;word-break:normal}.chx p{margin:0}.chx b{font-weight:600}.chx .ltr{direction:ltr;unicode-bidi:embed;unicode-bidi:isolate;display:inline-block}" +
    ".chx .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:36px;padding:0 14px;border-radius:var(--ch-r);font:inherit;font-size:14px;font-weight:500;cursor:pointer;white-space:nowrap;border:1px solid var(--ch-bd);background:transparent;color:inherit;transition:background .15s,opacity .15s}" +
    ".chx .btn:hover{background:var(--ch-mu)}.chx .btn:disabled{opacity:.5;pointer-events:none}.chx .btn svg{width:16px;height:16px;flex:none}" +
    ".chx .btn.pri{background:var(--ch-pr);color:var(--ch-pf);border-color:transparent}.chx .btn.pri:hover{opacity:.9}" +
    ".chx .btn.red{background:#e5484d;color:#fff;border-color:transparent}.chx .btn.ic{width:36px;padding:0}.chx .btn.sm{height:32px;padding:0 10px;font-size:13px}" +
    ".chx input{width:100%;height:36px;padding:0 12px;border-radius:var(--ch-r);border:1px solid var(--ch-bd);background:transparent;color:inherit;font:inherit;font-size:14px;outline:none;transition:box-shadow .15s}" +
    ".chx input:focus{box-shadow:0 0 0 2px var(--ch-bg),0 0 0 4px var(--ch-pr)}.chx input::placeholder{color:var(--ch-mf)}.chx input.ltr:placeholder-shown{direction:rtl;text-align:right}" +
    ".chx label{display:block;font-size:14px;font-weight:500;margin:0 0 6px}.chx .hint{font-size:12.5px;color:var(--ch-mf);margin-top:6px;line-height:1.7}" +
    ".chx .fld{margin-bottom:14px}.chx .mut{color:var(--ch-mf)}.chx .ltr{direction:ltr;unicode-bidi:embed;unicode-bidi:isolate}" +
    ".chx .err{font-size:13px;color:#e5484d;margin-top:10px;display:none;line-height:1.7}.chx .err.on{display:block}" +
    /* dialog */
    ".chp .chbk{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 12px 0 10px;margin:0 0 14px;border-radius:var(--ch-r);border:1px solid var(--ch-bd);background:transparent;color:var(--ch-mf);font:inherit;font-size:13px;line-height:1;cursor:pointer;white-space:nowrap}.chp .chbk:hover{background:var(--ch-mu);color:inherit}.chp .chbk svg{width:16px;height:16px;flex:none}" +
    ".chd,.chm,.chd *,.chm *{pointer-events:auto}" +
    ".chd{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(0,0,0,.8);opacity:0;transition:opacity .15s}.chd.on{opacity:1}" +
    ".chd .dl{width:100%;max-width:440px;max-height:calc(100vh - 32px);overflow:auto;background:var(--ch-bg);border:1px solid var(--ch-bd);border-radius:calc(var(--ch-r) + 4px);padding:24px;position:relative;transform:scale(.96);transition:transform .15s;box-shadow:0 20px 50px -12px rgba(0,0,0,.5)}.chd.on .dl{transform:none}" +
    ".chd h2{font-size:18px;font-weight:600;margin:0 0 6px;line-height:1.5;padding-inline-end:32px}.chd .ds{font-size:14px;color:var(--ch-mf);margin:0 0 20px;line-height:1.85}" +
    ".chd .cl{position:absolute;top:14px;inset-inline-end:14px;width:28px;height:28px;border:0;background:transparent;color:var(--ch-mf);cursor:pointer;border-radius:6px;display:grid;place-items:center}.chd .cl:hover{color:var(--ch-fg);background:var(--ch-mu)}.chd .cl svg{width:16px;height:16px}" +
    ".chd .ft{display:flex;gap:8px;justify-content:flex-end;margin-top:22px;flex-wrap:wrap-reverse}@media(max-width:480px){.chd .ft .btn{flex:1}}" +
    /* page */
    ".chp{padding:16px;max-width:100%}@media(min-width:768px){.chp{padding:24px}}" +
    ".chp{max-width:1100px}.chp .hd{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:20px}.chp .hd .hx,.chp .hd>div:first-child{flex:1 1 260px;min-width:0}.chp h1{font-size:24px;font-weight:700;margin:0;line-height:1.4}.chp .hd p{margin:6px 0 0;font-size:14px;line-height:1.8;color:var(--ch-mf)}" +
    ".chp .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:16px}@media(min-width:900px){.chp .stats{grid-template-columns:repeat(4,minmax(0,1fr))}}" +
    ".chp .card{background:var(--ch-card);border:1px solid var(--ch-bd);border-radius:calc(var(--ch-r) + 4px)}" +
    ".chp .stat{padding:16px}.chp .stat .t{display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:500;color:var(--ch-mf)}.chp .stat .t svg{width:16px;height:16px}.chp .stat b{display:block;font-size:22px;font-weight:700;margin-top:8px;direction:ltr;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
    ".chp .bar{display:flex;gap:8px;align-items:center;padding:12px;border-bottom:1px solid var(--ch-bd)}.chp .bar .s{position:relative;flex:1;max-width:320px}.chp .bar .s svg{position:absolute;top:10px;inset-inline-start:10px;width:16px;height:16px;color:var(--ch-mf)}.chp .bar .s input{padding-inline-start:34px}" +
    ".chp table{width:100%;border-collapse:collapse;font-size:14px}.chp th{text-align:start;font-weight:500;color:var(--ch-mf);height:42px;padding:0 14px;border-bottom:1px solid var(--ch-bd);white-space:nowrap}" +
    ".chp td{padding:12px 14px;border-bottom:1px solid var(--ch-bd);vertical-align:middle}.chp tr:last-child td{border-bottom:0}.chp tbody tr{transition:background .15s}.chp tbody tr:hover{background:var(--ch-mu)}" +
    ".chp .un{display:flex;align-items:center;gap:10px;min-width:0}.chp .av{width:32px;height:32px;border-radius:999px;display:grid;place-items:center;font-size:12px;font-weight:700;background:var(--ch-mu);flex:none;direction:ltr;text-transform:uppercase}.chp .un b{font-weight:600;direction:ltr;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
    ".chp .bdg{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;padding:2px 10px;border-radius:999px;border:1px solid transparent;white-space:nowrap}.chp .bdg i{width:6px;height:6px;border-radius:50%;background:currentColor}.chp .bdg.on{color:#30a46c;background:rgba(48,164,108,.12)}.chp .bdg.off{color:#e5484d;background:rgba(229,72,77,.12)}" +
    ".chp .use{min-width:150px}.chp .use .n{display:flex;justify-content:space-between;font-size:12.5px;direction:ltr;margin-bottom:6px}.chp .use .n span:last-child{color:var(--ch-mf)}.chp .pg{height:6px;border-radius:99px;background:var(--ch-mu);overflow:hidden}.chp .pg i{display:block;height:100%;border-radius:inherit;background:var(--ch-pr);transition:width .5s}.chp .pg i.hi{background:#e5484d}" +
    ".chp .tw{overflow-x:auto;-webkit-overflow-scrolling:touch}.chp .tw table{min-width:640px}.chp .mob{display:none}@media(max-width:767px){.chp .tw{display:none}.chp .mob{display:block}}" +
    ".chp .mi{padding:14px;border-bottom:1px solid var(--ch-bd)}.chp .mi:last-child{border-bottom:0}.chp .mi .r{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px}" +
    ".chp .empty{padding:48px 16px;text-align:center}.chp .empty .ei{width:48px;height:48px;border-radius:999px;background:var(--ch-mu);display:grid;place-items:center;margin:0 auto 12px}.chp .empty .ei svg{width:22px;height:22px}.chp .empty b{display:block;font-size:16px;margin-bottom:4px}.chp .empty p{margin:0 0 16px;font-size:14px;color:var(--ch-mf)}" +
    ".chp .sk{height:14px;border-radius:6px;background:var(--ch-mu);animation:chpk 1.2s ease-in-out infinite}@keyframes chpk{50%{opacity:.45}}" +
    /* dropdown */
    ".chm{position:fixed;z-index:2147483001;min-width:190px;padding:4px;background:var(--ch-bg);border:1px solid var(--ch-bd);border-radius:var(--ch-r);box-shadow:0 10px 30px -8px rgba(0,0,0,.35);opacity:0;transform:translateY(-4px);transition:opacity .12s,transform .12s}.chm.on{opacity:1;transform:none}" +
    ".chm button{display:flex;align-items:center;gap:10px;width:100%;height:34px;padding:0 10px;border:0;background:transparent;color:inherit;font:inherit;font-size:14px;border-radius:calc(var(--ch-r) - 2px);cursor:pointer;text-align:start}.chm button:hover{background:var(--ch-mu)}.chm button svg{width:16px;height:16px;flex:none;opacity:.8}.chm button.red{color:#e5484d}.chm hr{border:0;border-top:1px solid var(--ch-bd);margin:4px -4px}" +
    /* toast */
    ".cht{position:fixed;z-index:2147483002;bottom:20px;inset-inline-end:20px;max-width:calc(100vw - 40px);display:flex;align-items:center;gap:10px;padding:12px 16px;background:var(--ch-bg);border:1px solid var(--ch-bd);border-radius:var(--ch-r);box-shadow:0 10px 30px -8px rgba(0,0,0,.35);font-size:14px;opacity:0;transform:translateY(8px);transition:.2s}.cht.on{opacity:1;transform:none}.cht svg{width:18px;height:18px;flex:none}.cht.good svg{color:#30a46c}.cht.bad svg{color:#e5484d}" +
    /* owner access (login) */
    ".chk .kbox{display:flex;gap:8px;align-items:stretch}.chk .kbox input{flex:1;min-width:0;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:15px;letter-spacing:.06em;text-transform:uppercase}" +
    ".chk .kbox .btn{flex:none;height:36px;font-size:13px;padding:0 12px}" +
    ".chk .pw{position:relative}.chk .pw input{padding-left:40px;padding-right:12px}.chk .pw button{position:absolute;top:4px;left:4px;right:auto;width:28px;height:28px;border:0;background:transparent;color:var(--ch-mf);cursor:pointer;display:grid;place-items:center;border-radius:6px}.chk .pw button svg{width:16px;height:16px}" +
    ".chk .two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}@media(max-width:420px){.chk .two{grid-template-columns:minmax(0,1fr)}}" +
    ".chk .stp{display:flex;gap:6px;margin:0 0 18px}.chk .stp i{flex:1;height:3px;border-radius:3px;background:var(--ch-mu);transition:background .3s}.chk .stp i.on{background:var(--ch-pr)}" +
    ".chk details{margin-top:4px;border:1px solid var(--ch-bd);border-radius:var(--ch-r);padding:0 12px}.chk summary{cursor:pointer;font-size:13px;font-weight:500;padding:10px 0;list-style:none;display:flex;justify-content:space-between;align-items:center}.chk summary::-webkit-details-marker{display:none}.chk summary::after{content:'+';color:var(--ch-mf)}.chk details[open] summary::after{content:'-'}" +
    ".chk details ol{margin:0 0 12px;padding-inline-start:18px;font-size:13px;color:var(--ch-mf);line-height:2}.chk details code{font-family:ui-monospace,Consolas,monospace;background:var(--ch-mu);padding:1px 6px;border-radius:4px;direction:ltr;display:inline-block}" +
    ".chk .sm{font-size:12px;margin-top:6px;display:flex;align-items:center;gap:6px;color:var(--ch-mf)}.chk .sm i{flex:1;height:4px;border-radius:4px;background:var(--ch-mu);overflow:hidden;display:flex}.chk .sm i b{display:block;height:100%;width:0;transition:width .25s,background .25s}" +
    ".chk .done{text-align:center;padding:8px 0 4px}.chk .done .ok{width:64px;height:64px;border-radius:999px;margin:0 auto 14px;display:grid;place-items:center;background:rgba(48,164,108,.12);color:#30a46c}.chk .done .ok svg{width:30px;height:30px;stroke-dasharray:30;stroke-dashoffset:30;animation:chkd .5s .1s ease forwards}@keyframes chkd{to{stroke-dashoffset:0}}" +
    ".chk .done b{display:block;font-size:18px;margin-bottom:6px}.chk .done p{margin:0;color:var(--ch-mf);font-size:14px;line-height:1.8}" +
    /* English (left-to-right) panel */
    "[dir=ltr].chx .pw input,[dir=ltr] .chx .pw input,.chx[dir=ltr] .pw input{padding-left:12px!important;padding-right:40px!important}[dir=ltr].chx .pw button,[dir=ltr] .pw button{left:auto!important;right:4px!important}" +
    "" +
    "[dir=ltr].chp .stat b,[dir=ltr] .chp .stat b,[dir=ltr] .chb .kp b{text-align:left}[dir=ltr] .chx input.ltr:placeholder-shown,[dir=ltr].chx input.ltr:placeholder-shown{direction:ltr;text-align:left}" +
    "[dir=ltr] .chb .tg::after{right:auto;left:2px}[dir=ltr] .chb .tg.on::after{transform:translateX(18px)}";
  function ucss() { if (!document.getElementById("ch-ui-css")) { var st = document.createElement("style"); st.id = "ch-ui-css"; st.textContent = UCSS; document.head.appendChild(st); } }
  var IC = {
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    more: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    ref: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-2.6-6.4L21 8M21 3v5h-5"/></svg>',
    users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/></svg>',
    act: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    db: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 3v18h18M7 16v-4M12 16V8M17 16v-7"/></svg>',
    addgb: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></svg>',
    gauge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m12 14 4-4M3.3 19a10 10 0 1 1 17.4 0"/></svg>',
    key: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6M15.5 7.5l3 3L22 7l-3-3"/></svg>',
    ban: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="m5.7 5.7 12.6 12.6"/></svg>',
    play: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m10 8 6 4-6 4z"/></svg>',
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/></svg>',
    trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5 10 17 19 7"/></svg>',
    alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>',
    eye: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>',
    eyeoff: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18M10.6 5.1A10 10 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-2.4 3.3M6.6 6.6C3.9 8.3 2 12 2 12s3.5 7 10 7a9.7 9.7 0 0 0 5.4-1.6M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>',
    paste: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>'
  };
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function fmtGB(b) { if (!b) return "0 GB"; var g = b / 1073741824; if (g >= 1024) return Math.round(g / 102.4) / 10 + " TB"; return (g >= 100 ? Math.round(g) : Math.round(g * 10) / 10) + " GB"; }
  function copyText(t) { try { if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(t); } catch (e) {}
    var a = document.createElement("textarea"); a.value = t; a.style.position = "fixed"; a.style.opacity = "0"; document.body.appendChild(a); a.select(); try { document.execCommand("copy"); } catch (e) {} document.body.removeChild(a); return Promise.resolve(); }
  var toastT;
  function toast(text, kind) {
    ucss(); var t = document.getElementById("ch-toast");
    if (!t) { t = document.createElement("div"); t.id = "ch-toast"; t.className = "chx cht"; document.body.appendChild(t); }
    t.dir = DIR();
    themeVars(t); t.className = "chx cht " + (kind || "good"); t.innerHTML = (kind === "bad" ? IC.alert : IC.check) + "<span></span>"; t.lastChild.textContent = text;
    requestAnimationFrame(function () { t.classList.add("on"); }); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 2600);
  }
  /* native-looking dialog. opts: title, desc, html, ok, okClass, cancel, onOk(root) -> Promise<bool close>, onOpen(root) */
  /* phone/browser Back button: closes the open CHOST menu, dialog or page first, never leaves the panel by surprise */
  var HIST = { ignore: 0 };
  function hpush(kind) { try { history.pushState({ chost: kind }, ""); } catch (e) {} }
  function hpop(kind) { try { if (history.state && history.state.chost === kind) { HIST.ignore++; history.back(); } } catch (e) {} }
  window.addEventListener("popstate", function () {
    if (HIST.ignore > 0) { HIST.ignore--; return; }
    var m = document.getElementById("ch-menu"); if (m && m._chClose) { m._chClose(true); return; }
    var ds = document.querySelectorAll(".chd"), top = ds.length ? ds[ds.length - 1] : null;
    if (top && top._chClose) { top._chClose(true); return; }
    if (PAGE) closePage(false, true);
  });
  function dialog(opts) {
    ucss();
    var ov = document.createElement("div"); ov.className = "chx chd"; ov.dir = DIR(); themeVars(ov);
    ov.innerHTML = '<div class="dl ' + (opts.cls || "") + T('" role="dialog" aria-modal="true"><button class="cl" type="button" aria-label="بستن">') + IC.x + '</button>' +
      '<h2></h2><p class="ds"></p><div class="bx">' + (opts.html || "") + '</div><div class="err"></div>' +
      '<div class="ft">' + (opts.cancel === false ? "" : '<button class="btn" type="button" data-k="no">' + (opts.cancel || T("انصراف")) + '</button>') +
      (opts.ok ? '<button class="btn ' + (opts.okClass || "pri") + '" type="button" data-k="ok">' + opts.ok + '</button>' : "") + '</div></div>';
    ov.querySelector("h2").textContent = opts.title || ""; var ds = ov.querySelector(".ds"); if (opts.desc) ds.textContent = opts.desc; else ds.style.display = "none";
    document.body.appendChild(ov); requestAnimationFrame(function () { ov.classList.add("on"); });
    var err = ov.querySelector(".err"), ok = ov.querySelector('[data-k="ok"]');
    var api = { root: ov, error: function (m) { err.textContent = m || ""; err.classList.toggle("on", !!m); }, close: close, ok: ok };
    var closed = false;
    function close(fromPop) { if (closed) return; closed = true; ov._chClose = null; ov.classList.remove("on"); document.removeEventListener("keydown", key, true);
      setTimeout(function () { if (ov.parentNode) ov.parentNode.removeChild(ov); }, 160); if (fromPop !== true) hpop("dlg"); if (opts.onClose) opts.onClose(); }
    ov._chClose = close; hpush("dlg");
    function key(e) { if (e.key === "Escape") { e.stopPropagation(); close(); } if (e.key === "Enter" && ok && e.target.tagName === "INPUT") { e.preventDefault(); ok.click(); } }
    document.addEventListener("keydown", key, true);
    var downOnBg = false;
    ov.addEventListener("mousedown", function (e) { downOnBg = e.target === ov; });
    ov.addEventListener("click", function (e) { if (e.target === ov && downOnBg !== false) close(); downOnBg = null; });
    ov.querySelector(".cl").onclick = function () { close(); }; var no = ov.querySelector('[data-k="no"]'); if (no) no.onclick = function () { close(); };
    if (ok) ok.onclick = function () {
      api.error(""); if (!opts.onOk) return close();
      if (ok.disabled) return;
      var label = ok.innerHTML; ok.disabled = true; ok.textContent = "…";
      Promise.resolve(opts.onOk(api)).then(function (r) { ok.disabled = false; ok.innerHTML = label; if (r) close(); })
        .catch(function () { ok.disabled = false; ok.innerHTML = label; api.error(T("ارتباط با سرور برقرار نشد")); });
    };
    if (opts.onOpen) opts.onOpen(api);
    setTimeout(function () { var f = ov.querySelector("input"); if (f) f.focus(); }, 60);
    return api;
  }
  function menu(anchor, items) {
    ucss(); var old = document.getElementById("ch-menu"); if (old) old.parentNode.removeChild(old);
    var m = document.createElement("div"); m.id = "ch-menu"; m.className = "chx chm"; m.dir = DIR(); themeVars(m);
    m.innerHTML = items.map(function (it, i) { return it === "-" ? "<hr>" : '<button type="button" data-i="' + i + '" class="' + (it.red ? "red" : "") + '">' + it.icon + "<span>" + it.label + "</span></button>"; }).join("");
    document.body.appendChild(m);
    var r = anchor.getBoundingClientRect(), w = m.offsetWidth, h = m.offsetHeight;
    var left = Math.min(Math.max(8, r.left), window.innerWidth - w - 8), top = r.bottom + 6; if (top + h > window.innerHeight - 8) top = Math.max(8, r.top - h - 6);
    m.style.left = left + "px"; m.style.top = top + "px"; requestAnimationFrame(function () { m.classList.add("on"); });
    var done = false;
    function off(e) { if (!m.contains(e.target) && e.target !== anchor && !(anchor.contains && anchor.contains(e.target))) close(); }
    function esc(e) { if (e.key === "Escape") { e.stopPropagation(); close(); } }
    function close(fromPop) { if (done) return; done = true; m._chClose = null;
      document.removeEventListener("mousedown", off, true); document.removeEventListener("touchstart", off, true); document.removeEventListener("keydown", esc, true);
      window.removeEventListener("scroll", onScroll, true); window.removeEventListener("resize", onScroll, true); if (m.parentNode) m.parentNode.removeChild(m); if (fromPop !== true) hpop("menu"); }
    function onScroll() { close(); }
    m._chClose = close; hpush("menu");
    setTimeout(function () { document.addEventListener("mousedown", off, true); document.addEventListener("touchstart", off, true); document.addEventListener("keydown", esc, true);
      window.addEventListener("scroll", onScroll, true); window.addEventListener("resize", onScroll, true); }, 0);
    Array.prototype.forEach.call(m.querySelectorAll("button"), function (b) { b.onclick = function () { var it = items[+b.getAttribute("data-i")]; close(); setTimeout(function () { it.run(); }, 30); }; });
  }

  /* ---------- 4) sidebar "پنل نمایندگی": a real page inside the panel layout (owner only) ---------- */
  var RS_LABEL = "پنل نمایندگی";
  var RS_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/></svg>';
  var PAGE = null;   // {host, hidden:[], path, item}
  function api(path, body) { return post("/chost/resellers" + path, body || {}, findToken()); }
  var BOT_LABEL = "ربات تلگرام", SEC_LABEL = "امنیت حساب";
  var BOT_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.2 4.2 2.9 11.3c-.9.4-.9 1.1.1 1.4l4.6 1.4 1.8 5.5c.2.6.6.7 1.1.3l2.6-2.1 4.8 3.5c.7.4 1.3.2 1.5-.7l3-14.2c.3-1.2-.4-1.7-1.2-1.2Z"/><path d="m7.6 14.1 9.6-6.1"/></svg>';
  var SEC_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-3.6 8-10V5l-8-3-8 3v7c0 6.4 8 10 8 10Z"/><rect x="9" y="10.5" width="6" height="5" rx="1"/><path d="M10.5 10.5V9a1.5 1.5 0 0 1 3 0v1.5"/></svg>';
  var PAGES = {
    rs:  { label: RS_LABEL,  icon: RS_ICON,  owner: true,  render: function (h) { renderPage(h); } },
    bot: { label: BOT_LABEL, icon: BOT_ICON, owner: true,  render: function (h) { renderBotPage(h); } },
    sec: { label: SEC_LABEL, icon: SEC_ICON, owner: false, render: function (h) { renderSecPage(h); } }
  };
  var ORDER = ["rs", "bot", "sec"];
  function pageOpen(key) { return !!(PAGE && document.body.contains(PAGE.host) && (!key || PAGE.key === key)); }
  var resellerPageOpen = function () { return pageOpen("rs"); };
  function itemBtns(key) { return Array.prototype.map.call(document.querySelectorAll('[data-ch="' + key + '"]'), function (li) { return li.querySelector('[data-sidebar="menu-button"], a, button') || li; }); }
  function setActive(key, on) { itemBtns(key).forEach(function (b) { b.setAttribute("data-active", on ? "true" : "false"); }); }
  function closePage(routed, fromPop, keepHist) {
    if (!PAGE) return;
    var mn = document.getElementById("ch-menu"); if (mn && mn._chClose) mn._chClose(true);
    if (routed) PAGE.activeOff = [];
    PAGE.hidden.forEach(function (el) { el.style.display = el.getAttribute("data-ch-disp") || ""; el.removeAttribute("data-ch-disp"); el.removeAttribute("data-ch-hid"); });
    if (PAGE.host.parentNode) PAGE.host.parentNode.removeChild(PAGE.host);
    setActive(PAGE.key, false);
    (PAGE.activeOff || []).forEach(function (x) { if (document.body.contains(x)) x.setAttribute("data-active", "true"); });
    clearInterval(botTimer); PAGE = null;
    if (!routed && !fromPop && !keepHist) hpop("page");
  }
  var closeResellerPage = closePage;
  function openPage(key) {
    if (pageOpen(key)) { closeSidebar(); return; }
    var activeOff = PAGE ? PAGE.activeOff : null;
    var wasPage = !!PAGE;
    if (PAGE) { PAGE.activeOff = []; closePage(false, false, true); }
    var main = document.querySelector("main"); if (!main) return;
    ucss(); bcss(); closeSidebar();
    var hidden = [], keep = [], trig = main.querySelector('[data-sidebar="trigger"]');
    if (trig) { var hd = null, n = trig; while (n && n !== main) { if (String(n.tagName).toUpperCase() === "HEADER") hd = n; n = n.parentElement; }
      if (!hd) hd = trig;
      for (n = hd; n && n !== main; n = n.parentElement) keep.push(n); keep.reverse(); }   /* main > ... > header: stays visible */
    function hideAround(parent, skip) { Array.prototype.forEach.call(parent.children, function (c) { if (c === skip || c.getAttribute("data-ch-page")) return;
      c.setAttribute("data-ch-disp", c.style.display || ""); c.setAttribute("data-ch-hid", "1"); c.style.display = "none"; hidden.push(c); }); }
    var host = document.createElement("div"); host.id = "ch-pg-" + key; host.setAttribute("data-ch-page", key); host.className = "chx chp"; host.dir = DIR(); themeVars(host);
    if (keep.length) { var par = main; keep.forEach(function (k) { hideAround(par, k); par = k; }); var last = keep[keep.length - 1];
      last.parentNode.insertBefore(host, last.nextSibling); }
    else { hideAround(main, null); main.appendChild(host); }
    if (!activeOff) { activeOff = [];
      Array.prototype.forEach.call(document.querySelectorAll('[data-sidebar="menu-button"][data-active="true"]'), function (b) { if (!b.closest("[data-ch]")) { b.setAttribute("data-active", "false"); activeOff.push(b); } }); }
    ORDER.forEach(function (k) { setActive(k, k === key); });
    PAGE = { key: key, host: host, hidden: hidden, path: location.pathname + location.search + location.hash, activeOff: activeOff };
    if (!wasPage && !(history.state && history.state.chost === "page")) hpush("page");
    try { window.scrollTo(0, 0); main.scrollTop = 0; } catch (e) {}
    try { PAGES[key].render(host); addBack(host); } catch (e) { host.innerHTML = T('<div class="card"><div class="empty"><b>این بخش بارگذاری نشد</b><p>صفحه را یک بار تازه کنید.</p></div></div>'); }
  }
  function addBack(host) {   /* always a clear way out of a CHOST page, on phone and desktop */
    var bk = document.createElement("button"); bk.type = "button"; bk.className = "chbk";
    bk.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="' + (DIR() === "rtl" ? "m9 6 6 6-6 6" : "m15 6-6 6 6 6") + '"/></svg><span>' + T("بازگشت") + "</span>";
    bk.onclick = function () { closePage(); try { window.scrollTo(0, 0); } catch (e) {} };
    host.insertBefore(bk, host.firstChild);
  }
  function pageHead(title, desc, btn) {
    return '<div class="hd"><div class="hx"><h1>' + title + '</h1><p>' + desc + '</p></div>' + (btn || "") + '</div>';
  }
  function renderBotPage(host) {
    host.innerHTML = pageHead(T(BOT_LABEL), T("فروش خودکار اشتراک در تلگرام؛ کیف پول، خرید فوری، سیستم دعوت با پورسانت، کد تخفیف، اکانت تست، یادآوری تمدید و بکاپ روزانه."));
    botCard(host);
    var g = document.createElement("section"); g.className = "chx chb"; g.dir = DIR(); themeVars(g);
    g.innerHTML = '<div class="top"><div class="lg pr">' + IC.check + T('</div><div class="tt"><b>راه‌اندازی در چهار قدم</b><p>کمتر از دو دقیقه زمان می‌برد.</p></div></div>') +
      '<ol class="steps">' +
      T('<li><b>ساخت ربات</b><span>در تلگرام به <span class="ltr">@BotFather</span> پیام دهید، دستور <span class="ltr">/newbot</span> را بفرستید و توکن ربات را کپی کنید.</span></li>') +
      T('<li><b>آیدی عددی مدیر</b><span>آیدی عددی خود را از ربات <span class="ltr">@userinfobot</span> دریافت کنید.</span></li>') +
      T('<li><b>ذخیره در پنل</b><span>توکن و آیدی را در کادر بالا وارد کنید، ربات را فعال کنید و «ذخیره» را بزنید.</span></li>') +
      T('<li><b>تنظیمات فروش</b><span>ربات را در تلگرام Start کنید و دستور <span class="ltr">/admin</span> را بفرستید تا پلن‌ها، قیمت‌ها و شماره کارت را تنظیم کنید.</span></li></ol>');
    host.appendChild(g);
  }
  function renderSecPage(host) {
    host.innerHTML = pageHead(T(SEC_LABEL), OWNER === true ? T("رمز عبور حساب خود را تغییر دهید و در صورت نیاز کلید دسترسی مالک بسازید.") : T("رمز عبور حساب خود را تغییر دهید."));
    passCard(host);
    if (OWNER === true) keyCard(host);
  }
  function openResellerPage() { openPage("rs"); }
  function closeSidebar() { try { var o = document.querySelector('[data-sidebar="sidebar"][data-mobile="true"]'); if (o) document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); } catch (e) {} }

  function renderPage(host) {
    host.innerHTML =
      '<div class="hd"><div><h1>' + T(RS_LABEL) + T('</h1><p>برای هر نماینده یک پنل جدا با سهمیه‌ی حجم بسازید. نماینده با همین آدرس وارد می‌شود و فقط کاربران خودش را می‌بیند.</p></div>') +
      '<button class="btn pri" type="button" data-a="new">' + IC.plus + T('<span>نماینده‌ی جدید</span></button></div>') +
      '<div class="stats">' +
        T('<div class="card stat"><div class="t"><span>نماینده‌ها</span>') + IC.users + '</div><b data-s="n">-</b></div>' +
        T('<div class="card stat"><div class="t"><span>فعال</span>') + IC.act + '</div><b data-s="a">-</b></div>' +
        T('<div class="card stat"><div class="t"><span>کل سهمیه</span>') + IC.db + '</div><b data-s="q">-</b></div>' +
        T('<div class="card stat"><div class="t"><span>کل مصرف</span>') + IC.chart + '</div><b data-s="u">-</b></div></div>' +
      '<div class="card"><div class="bar"><div class="s">' + IC.search + T('<input type="search" placeholder="جست‌وجوی نماینده" data-a="q"></div><div style="flex:1"></div><button class="btn ic" type="button" title="به‌روزرسانی" data-a="ref">') + IC.ref + '</button></div>' +
      '<div data-a="body"></div></div>';
    var body = host.querySelector('[data-a="body"]'), q = host.querySelector('[data-a="q"]'), all = [];
    host.querySelector('[data-a="new"]').onclick = function () { createDialog(load); };
    host.querySelector('[data-a="ref"]').onclick = function () { load(true); };
    q.oninput = function () { draw(); };
    function skeleton() { var r = ""; for (var i = 0; i < 3; i++) r += '<div class="mi"><div class="sk" style="width:' + (40 + i * 15) + '%"></div><div class="sk" style="width:80%;margin-top:10px;height:8px"></div></div>'; body.innerHTML = r; }
    function stat(k, v) { var el = host.querySelector('[data-s="' + k + '"]'); if (el) el.textContent = v; }
    function draw() {
      var term = q.value.trim().toLowerCase(), rs = all.filter(function (r) { return !term || String(r.username).toLowerCase().indexOf(term) > -1; });
      var qq = 0, uu = 0, act = 0; all.forEach(function (r) { qq += r.limit || 0; uu += r.used || 0; if (!r.disabled) act++; });
      stat("n", all.length); stat("a", act); stat("q", fmtGB(qq)); stat("u", fmtGB(uu));
      if (!all.length) { body.innerHTML = '<div class="empty"><div class="ei">' + IC.users + T('</div><b>هنوز نماینده‌ای ندارید</b><p>اولین پنل نمایندگی را بسازید و اطلاعات ورود را برای نماینده بفرستید.</p><button class="btn pri" type="button" data-a="new2">') + IC.plus + T('<span>نماینده‌ی جدید</span></button></div>');
        body.querySelector('[data-a="new2"]').onclick = function () { createDialog(load); }; return; }
      if (!rs.length) { body.innerHTML = T('<div class="empty"><b>نتیجه‌ای پیدا نشد</b><p>نام دیگری را جست‌وجو کنید.</p></div>'); return; }
      function use(r) { var p = r.limit ? Math.min(100, Math.round(r.used / r.limit * 100)) : 0;
        return '<div class="use"><div class="n"><span>' + fmtGB(r.used) + " / " + (r.limit ? fmtGB(r.limit) : "∞") + '</span><span>' + (r.limit ? p + "%" : "") + '</span></div><div class="pg"><i class="' + (p >= 90 ? "hi" : "") + '" style="width:' + (r.limit ? p : 0) + '%"></i></div></div>'; }
      function badge(r) { return '<span class="bdg ' + (r.disabled ? "off" : "on") + '"><i></i>' + (r.disabled ? T("غیرفعال") : T("فعال")) + "</span>"; }
      function who(r) { return '<div class="un"><div class="av">' + esc(String(r.username).slice(0, 2)) + '</div><b>' + esc(r.username) + "</b></div>"; }
      var more = T('<button class="btn ic sm" type="button" data-m="1" aria-label="عملیات">') + IC.more + "</button>";
      body.innerHTML = T('<div class="tw"><table><thead><tr><th>نام کاربری</th><th>وضعیت</th><th>مصرف / سهمیه</th><th>کاربران</th><th style="width:56px"></th></tr></thead><tbody>') +
        rs.map(function (r, i) { return '<tr data-i="' + i + '"><td>' + who(r) + "</td><td>" + badge(r) + "</td><td>" + use(r) + '</td><td class="ltr">' + (r.users || 0) + "</td><td>" + more + "</td></tr>"; }).join("") + "</tbody></table></div>" +
        '<div class="mob">' + rs.map(function (r, i) { return '<div class="mi" data-i="' + i + '"><div class="r">' + who(r) + '<div style="display:flex;gap:6px;align-items:center">' + badge(r) + more + "</div></div>" + use(r) + "</div>"; }).join("") + "</div>";
      Array.prototype.forEach.call(body.querySelectorAll('[data-m="1"]'), function (b) {
        var r = rs[+b.closest("[data-i]").getAttribute("data-i")];
        b.onclick = function (e) { e.stopPropagation(); rowMenu(b, r, load); };
      });
    }
    function load(manual) {
      if (!all.length) skeleton();
      return api("", {}).then(function (x) {
        if (x[0] !== 200) { body.innerHTML = T('<div class="empty"><b>بارگذاری نشد</b><p>') + esc(x[1].detail || T("دوباره امتحان کنید")) + "</p></div>"; return; }
        all = x[1].resellers || []; draw(); if (manual) toast(T("فهرست به‌روزرسانی شد"));
      }).catch(function () { body.innerHTML = T('<div class="empty"><b>ارتباط با سرور برقرار نشد</b><p>اتصال اینترنت را بررسی کنید و دوباره امتحان کنید.</p></div>'); });
    }
    load();
  }
  function loginInfo(u, p, gb) { return T("پنل نمایندگی CHOST\nآدرس: ") + location.origin + T("/dashboard/\nنام کاربری: ") + u + T("\nرمز عبور: ") + p + T("\nسهمیه: ") + (gb ? gb + " GB" : T("نامحدود")); }
  function createDialog(done) {
    dialog({ title: T("نماینده‌ی جدید"), desc: T("یک پنل نمایندگی با سهمیه‌ی حجم بسازید. نماینده فقط با قالب‌های آماده کاربر می‌سازد."), ok: T("ساخت پنل نمایندگی"),
      html: T('<div class="fld"><label>نام کاربری</label><input class="ltr" data-f="u" autocomplete="off" spellcheck="false" placeholder="reseller1"><div class="hint">حروف انگلیسی، عدد و _ (3 تا 32 کاراکتر)</div></div>') +
            T('<div class="fld"><label>رمز عبور</label><input class="ltr" data-f="p" autocomplete="new-password" spellcheck="false" placeholder="حداقل 4 کاراکتر"></div>') +
            T('<div class="fld" style="margin:0"><label>سهمیه‌ی حجم (گیگابایت)</label><input class="ltr" data-f="g" type="number" inputmode="decimal" min="0" step="any" value="50"><div class="hint">0 یعنی نامحدود. وقتی سهمیه تمام شود، کاربران نماینده خودکار متوقف می‌شوند.</div></div>'),
      onOk: function (d) {
        var R = d.root, u = R.querySelector('[data-f="u"]').value.trim(), p = R.querySelector('[data-f="p"]').value, gv = R.querySelector('[data-f="g"]').value, g = gv === "" ? 0 : +gv;
        if (!/^[A-Za-z0-9_]{3,32}$/.test(u)) { d.error(T("نام کاربری باید فقط شامل حروف انگلیسی، عدد و _ و بین 3 تا 32 کاراکتر باشد")); return false; }
        if (p.length < 4) { d.error(T("رمز عبور باید حداقل 4 کاراکتر باشد")); return false; }
        if (!(g >= 0)) { d.error(T("سهمیه را درست وارد کنید")); return false; }
        return api("/create", { username: u, password: p, gb: g }).then(function (x) {
          if (x[0] !== 200) { d.error(x[1].detail || T("ساخت ممکن نشد")); return false; }
          done(); setTimeout(function () { infoDialog(u, p, g); }, 180); return true;
        });
      } });
  }
  function infoDialog(u, p, g) {
    var info = loginInfo(u, p, g);
    dialog({ title: T("پنل نمایندگی ساخته شد"), desc: T("این اطلاعات را برای نماینده بفرستید. رمز عبور بعداً نمایش داده نمی‌شود."), ok: IC.copy + T("<span>کپی اطلاعات ورود</span>"), cancel: T("بستن"),
      html: '<div class="card" style="border:1px solid var(--ch-bd);border-radius:var(--ch-r);padding:14px;background:var(--ch-mu);font-size:13.5px;line-height:2;white-space:pre-wrap;word-break:break-all"></div>',
      onOpen: function (d) { d.root.querySelector(".card").textContent = info; },
      onOk: function () { return copyText(info).then(function () { toast(T("اطلاعات ورود کپی شد")); return true; }); } });
  }
  function rowMenu(anchor, r, reload) {
    function upd(action, extra, okMsg) { var b = { username: r.username, action: action }; for (var k in extra) b[k] = extra[k];
      return api("/update", b).then(function (x) { if (x[0] !== 200) return x[1].detail || T("انجام نشد"); toast(okMsg); reload(); return null; }); }
    function gbDialog(mode) {
      var add = mode === "add_gb";
      dialog({ title: add ? T("افزایش سهمیه") : T("تنظیم سهمیه"), desc: (add ? T("حجم اضافه برای ") : T("سهمیه‌ی جدید برای ")) + r.username + (r.limit ? T(" (فعلی: ") + fmtGB(r.limit) + ")" : T(" (فعلی: نامحدود)")), ok: T("ذخیره"),
        html: '<div class="fld" style="margin:0"><label>' + (add ? T("حجم اضافه (گیگابایت)") : T("سهمیه (گیگابایت)")) + '</label><input class="ltr" data-f="g" type="number" inputmode="decimal" min="0" step="any" placeholder="' + (add ? T("مثلاً 50") : T("0 = نامحدود")) + '">' + (add ? "" : T('<div class="hint">0 یعنی نامحدود.</div>')) + "</div>",
        onOk: function (d) { var v = d.root.querySelector('[data-f="g"]').value, n = v === "" ? NaN : +v;
          if (!(n >= 0) || (add && !(n > 0))) { d.error(T("مقدار را درست وارد کنید")); return false; }
          return upd(mode, { gb: n }, T("سهمیه ذخیره شد")).then(function (e) { if (e) { d.error(e); return false; } return true; }); } });
    }
    var items = [];
    if (r.limit) items.push({ icon: IC.addgb, label: T("افزایش سهمیه"), run: function () { gbDialog("add_gb"); } });
    items.push({ icon: IC.gauge, label: T("تنظیم سهمیه"), run: function () { gbDialog("set_gb"); } });
    items.push({ icon: IC.key, label: T("تغییر رمز عبور"), run: function () {
      dialog({ title: T("تغییر رمز عبور"), desc: T("رمز جدید برای ") + r.username, ok: T("ذخیره"),
        html: T('<div class="fld" style="margin:0"><label>رمز جدید</label><input class="ltr" data-f="p" autocomplete="new-password" spellcheck="false" placeholder="حداقل 4 کاراکتر"></div>'),
        onOk: function (d) { var p = d.root.querySelector('[data-f="p"]').value; if (p.length < 4) { d.error(T("رمز عبور باید حداقل 4 کاراکتر باشد")); return false; }
          return upd("password", { password: p }, T("رمز عبور تغییر کرد")).then(function (e) { if (e) { d.error(e); return false; } setTimeout(function () { infoDialog(r.username, p, r.limit ? Math.round(r.limit / 1073741824 * 10) / 10 : 0); }, 180); return true; }); } });
    } });
    items.push({ icon: IC.copy, label: T("کپی آدرس پنل"), run: function () { copyText(location.origin + "/dashboard/").then(function () { toast(T("آدرس پنل کپی شد")); }); } });
    items.push(r.disabled ? { icon: IC.play, label: T("فعال کردن"), run: function () { upd("enable", {}, T("نماینده فعال شد")).then(function (e) { if (e) toast(e, "bad"); }); } }
                          : { icon: IC.ban, label: T("غیرفعال کردن"), run: function () { upd("disable", {}, T("نماینده غیرفعال شد")).then(function (e) { if (e) toast(e, "bad"); }); } });
    items.push("-");
    items.push({ icon: IC.trash, label: T("حذف نماینده"), red: true, run: function () {
      dialog({ title: T("حذف ") + r.username + T("؟"), desc: T("این نماینده حذف می‌شود و دیگر نمی‌تواند وارد پنل شود. این کار برگشت‌پذیر نیست."), ok: T("حذف"), okClass: "red",
        onOk: function (d) { return upd("delete", {}, T("نماینده حذف شد")).then(function (e) { if (e) { d.error(e); return false; } return true; }); } });
    } });
    menu(anchor, items);
  }
  function mountPages() {
    var authed = !!findToken();
    if (PAGE) {   // left the page through the router (back button, link, logo): give the panel its content back
      var main = document.querySelector("main"), pg = PAGES[PAGE.key];
      if (!main || !main.contains(PAGE.host) || PAGE.path !== location.pathname + location.search + location.hash || (pg.owner && OWNER !== true) || !authed) closePage(PAGE.path !== location.pathname + location.search + location.hash);
    }
    sidebars().forEach(function (side) { mountIn(side, authed); });
  }
  function isUsers(item) {
    var a = item.querySelector('[data-sidebar="menu-button"], a, button') || item, href = a.getAttribute("href") || "";
    if (/\/users?(\/|\?|#|$)/i.test(href)) return true;
    var t = label(a); return t === norm("کاربران") || t === norm("کاربرها") || t === "users";
  }
  function mountIn(side, authed) {
    var ref = null, items = side.querySelectorAll('[data-sidebar="menu-item"]');
    for (var i = 0; i < items.length; i++) {
      if (items[i].getAttribute("data-ch") || items[i].getAttribute("data-jx") === "hidden") continue;
      if (isUsers(items[i])) { ref = items[i]; break; }
    }
    var prev = ref;
    ORDER.forEach(function (key) {
      var pg = PAGES[key], mine = side.querySelector('[data-ch="' + key + '"]');
      var show = authed && (pg.owner ? OWNER === true : OWNER !== null);
      if (!show) { if (mine && mine.parentNode) mine.parentNode.removeChild(mine); return; }
      if (mine) { var lb = mine.querySelector("span, p"); if (lb && lb.textContent !== T(pg.label)) lb.textContent = T(pg.label); prev = mine; return; }
      if (!ref) return;
      var clone = ref.cloneNode(true); clone.removeAttribute("id"); clone.setAttribute("data-ch", key); clone.style.display = "";
      Array.prototype.forEach.call(clone.querySelectorAll('[data-sidebar="menu-sub"], [data-sidebar="menu-action"], [data-sidebar="menu-badge"], ul ul'), function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
      Array.prototype.forEach.call(clone.querySelectorAll("[id]"), function (n) { n.removeAttribute("id"); });
      var btn = clone.querySelector('[data-sidebar="menu-button"], a, button') || clone;
      btn.removeAttribute("href"); btn.removeAttribute("aria-current"); btn.removeAttribute("data-state"); btn.setAttribute("data-active", pageOpen(key) ? "true" : "false");
      btn.setAttribute("role", "button"); btn.setAttribute("tabindex", "0");
      var svgs = btn.querySelectorAll("svg");
      if (svgs.length) { var tmp = document.createElement("div"); tmp.innerHTML = pg.icon; var ns = tmp.firstChild; ns.setAttribute("class", svgs[0].getAttribute("class") || ""); svgs[0].parentNode.replaceChild(ns, svgs[0]);
        for (var k = 1; k < svgs.length; k++) if (svgs[k].parentNode) svgs[k].parentNode.removeChild(svgs[k]); }
      var lab = btn.querySelector("span, p");
      if (lab) lab.textContent = T(pg.label); else btn.appendChild(document.createTextNode(T(pg.label)));
      var go = function (e) { e.preventDefault(); e.stopPropagation(); if (e.stopImmediatePropagation) e.stopImmediatePropagation(); openPage(key); };
      btn.addEventListener("click", go, true);
      btn.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") go(e); });
      if (prev && prev.parentNode) prev.parentNode.insertBefore(clone, prev.nextSibling);
      prev = clone;
    });
  }
  /* any other sidebar item closes the CHOST page (also when it points to the page you were on) */
  document.addEventListener("click", function (e) {
    if (!PAGE) return; var t = e.target && e.target.closest ? e.target.closest('[data-sidebar="menu-button"], [data-sidebar="menu-sub-button"], aside a, nav a') : null;
    if (t && !t.closest("[data-ch]")) closePage(false, false, true);   /* the panel itself navigates: keep its history as it is */
  }, true);

  /* ---------- 5) login page: "Owner access" with the CHOST owner key ---------- */
  var OWN_WORDS = ["دسترسی مالک", "owner access", "ورود مالک", "بازیابی دسترسی", "forgot password", "فراموشی رمز"].map(norm);
  function fmtKey(v) { var s = String(v || "").toUpperCase().replace(/[^A-Z0-9]/g, ""); if (s.indexOf("CH") === 0) s = s.slice(2); s = s.slice(0, 12); var p = []; for (var i = 0; i < s.length; i += 4) p.push(s.slice(i, i + 4)); return p.length ? "CH-" + p.join("-") : ""; }
  function strength(p) { var s = 0; if (p.length >= 4) s++; if (p.length >= 8) s++; if (/[A-Z]/.test(p) && /[a-z]/.test(p)) s++; if (/\d/.test(p) && /[^A-Za-z0-9]/.test(p)) s++; return s; }
  function ownerDialog() {
    var pwField = function (f, ph) { return '<div class="pw"><input class="ltr" data-f="' + f + '" type="password" autocomplete="new-password" spellcheck="false" placeholder="' + ph + T('"><button type="button" tabindex="-1" aria-label="نمایش رمز">') + IC.eye + "</button></div>"; };
    dialog({ cls: "chk", title: T("دسترسی مالک"), desc: T("با کلید مالک، نام کاربری و رمز پنل را از نو تنظیم کنید. هر کلید 5 دقیقه اعتبار دارد و فقط یک بار کار می‌کند."), ok: T("ثبت و ادامه"),
      html: '<div class="stp"><i class="on"></i><i></i><i></i></div>' +
        T('<div class="fld"><label>کلید مالک</label><div class="kbox"><input class="ltr" data-f="k" autocomplete="one-time-code" spellcheck="false" placeholder="CH-XXXX-XXXX-XXXX" maxlength="17"><button class="btn sm" type="button" data-f="paste">') + IC.paste + T("<span>چسباندن</span></button></div></div>") +
        T('<div class="fld"><label>نام کاربری</label><input class="ltr" data-f="u" autocomplete="username" spellcheck="false" value="admin"></div>') +
        T('<div class="two"><div class="fld"><label>رمز جدید</label>') + pwField("p", T("حداقل 4 کاراکتر")) + T('<div class="sm"><i><b data-f="bar"></b></i><span data-f="lvl"></span></div></div><div class="fld"><label>تکرار رمز</label>') + pwField("p2", T("دوباره وارد کنید")) + "</div></div>" +
        T('<details><summary>کلید مالک را از کجا بگیرم؟</summary><ol><li>اگر وارد پنل هستید: از منو، بخش <b>امنیت حساب</b> و دکمه‌ی «دریافت کلید».</li><li>اگر وارد نمی‌شوید: سرویس را در Railway ری‌استارت کنید و در لاگ‌ها خط <code>OWNER KEY</code> را پیدا کنید.</li></ol></details>'),
      onOpen: function (d) {
        var R = d.root, k = R.querySelector('[data-f="k"]'), p = R.querySelector('[data-f="p"]'), p2 = R.querySelector('[data-f="p2"]'), steps = R.querySelectorAll(".stp i");
        function prog() { var s = [fmtKey(k.value).length === 17, R.querySelector('[data-f="u"]').value.trim().length >= 3, p.value.length >= 4 && p.value === p2.value]; steps[1].classList.toggle("on", s[0]); steps[2].classList.toggle("on", s[0] && s[1] && s[2]); }
        k.addEventListener("input", function () { var c = k.selectionStart === k.value.length; k.value = fmtKey(k.value); if (c) k.selectionStart = k.selectionEnd = k.value.length; prog(); });
        R.querySelector('[data-f="paste"]').onclick = function () { try { navigator.clipboard.readText().then(function (t) { k.value = fmtKey(t); prog(); R.querySelector('[data-f="u"]').focus(); }).catch(function () { k.focus(); }); } catch (e) { k.focus(); } };
        var cols = ["#e5484d", "#f5a524", "#30a46c", "#30a46c"], names = [T("ضعیف"), T("متوسط"), T("خوب"), T("قوی")];
        p.addEventListener("input", function () { var s = strength(p.value), b = R.querySelector('[data-f="bar"]'); b.style.width = (p.value ? Math.max(1, s) * 25 : 0) + "%"; b.style.background = cols[Math.max(0, s - 1)]; R.querySelector('[data-f="lvl"]').textContent = p.value ? names[Math.max(0, s - 1)] : ""; prog(); });
        p2.addEventListener("input", prog); R.querySelector('[data-f="u"]').addEventListener("input", prog);
        Array.prototype.forEach.call(R.querySelectorAll(".pw button"), function (b) { b.onclick = function () { var i = b.previousSibling, show = i.type === "password"; i.type = show ? "text" : "password"; b.innerHTML = show ? IC.eyeoff : IC.eye; }; });
      },
      onOk: function (d) {
        var R = d.root, key = fmtKey(R.querySelector('[data-f="k"]').value), u = R.querySelector('[data-f="u"]').value.trim(), p = R.querySelector('[data-f="p"]').value, p2 = R.querySelector('[data-f="p2"]').value;
        if (key.length !== 17) { d.error(T("کلید مالک کامل نیست. قالب صحیح: CH-XXXX-XXXX-XXXX")); return false; }
        if (!/^[A-Za-z0-9_]{3,32}$/.test(u)) { d.error(T("نام کاربری باید فقط شامل حروف انگلیسی، عدد و _ و بین 3 تا 32 کاراکتر باشد")); return false; }
        if (p.length < 4) { d.error(T("رمز جدید باید حداقل 4 کاراکتر باشد")); return false; }
        if (p !== p2) { d.error(T("تکرار رمز با رمز جدید یکسان نیست")); return false; }
        return post("/chost/recover", { key: key, username: u, password: p }).then(function (x) {
          if (x[0] !== 200) { d.error(x[1].detail || T("ثبت ممکن نشد")); return false; }
          d.close(); setTimeout(function () { ownerDone(u); }, 180); return false;
        });
      } });
  }
  function ownerDone(u) {
    dialog({ cls: "chk", title: "", ok: T("ورود به پنل"), cancel: false,
      html: '<div class="done"><div class="ok">' + IC.check + T('</div><b>رمز پنل تنظیم شد</b><p>از این به بعد با نام کاربری <b class="ltr" style="display:inline;font-size:inherit"></b> و رمز جدید وارد شوید.</p></div>'),
      onOpen: function (d) { d.root.querySelector("h2").style.display = "none"; d.root.querySelector(".done p b").textContent = u; },
      onOk: function () {
        var f = document.querySelector('input[name="username"], input[autocomplete="username"], form input[type="text"]');
        if (f) { var set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set; set.call(f, u); f.dispatchEvent(new Event("input", { bubbles: true }));
          var pw = document.querySelector('form input[type="password"]'); if (pw) setTimeout(function () { pw.focus(); }, 200); }
        return true;
      } });
  }
  function onLoginPage() { return !findToken() && !!document.querySelector('input[type="password"]') && !document.querySelector('[data-sidebar="sidebar"]'); }
  function mountOwner() {
    if (!onLoginPage()) return;
    var cands = document.querySelectorAll("button, a, [role=button]"), hit = false;
    for (var i = 0; i < cands.length; i++) {
      var el = cands[i]; if (el.closest(".chd")) continue;
      if (OWN_WORDS.indexOf(norm(el.textContent)) > -1) { hit = true; if (!el.getAttribute("data-ch-own")) { el.setAttribute("data-ch-own", "1"); el.addEventListener("click", function (e) { e.preventDefault(); e.stopImmediatePropagation(); ownerDialog(); }, true); } }
    }
    if (hit || document.getElementById("ch-own-link")) return;
    var form = document.querySelector('form input[type="password"]'); form = form && form.closest("form"); if (!form) return;
    ucss(); var w = document.createElement("div"); w.id = "ch-own-link"; w.className = "chx"; w.dir = DIR(); themeVars(w);
    w.style.cssText = "text-align:center;margin-top:14px;font-size:13px";
    w.innerHTML = T('<a role="button" tabindex="0" style="cursor:pointer;color:var(--ch-mf);text-decoration:underline;text-underline-offset:4px">دسترسی مالک</a>');
    w.firstChild.onclick = ownerDialog; w.firstChild.onkeydown = function (e) { if (e.key === "Enter") ownerDialog(); };
    form.parentNode.insertBefore(w, form.nextSibling);
  }


  /* ---------- Telegram bot card (owner only), shown on the "Telegram bot" page ---------- */
  var BCSS = ".chb{margin:0 0 16px;padding:20px;background:var(--ch-card);border:1px solid var(--ch-bd);border-radius:calc(var(--ch-r) + 4px)}" +
    ".chb .top{display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;margin-bottom:18px}" +
    ".chb .lg{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#229ed9;color:#fff;flex:none}.chb .lg svg{width:22px;height:22px;flex:none;display:block}" +
    ".chb .tt{flex:1 1 240px;min-width:0}.chb .tt b{display:block;font-size:16px;font-weight:600;line-height:1.5}.chb .tt p{margin:4px 0 0;font-size:13.5px;color:var(--ch-mf);line-height:1.85}.chb .top>.btn,.chb .top>.pill{flex:none;margin-top:2px}" +
    ".chb .pill{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:600;padding:4px 11px;border-radius:999px;white-space:nowrap;max-width:100%;overflow:hidden}.chb .pill>span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
    ".chb .pill i{flex:none;width:7px;height:7px;border-radius:50%;background:currentColor}" +
    ".chb .pill.on{color:#30a46c;background:rgba(48,164,108,.12)}.chb .pill.off{color:var(--ch-mf);background:var(--ch-mu)}.chb .pill.bad{color:#e5484d;background:rgba(229,72,77,.12)}" +
    ".chb .kp{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:18px}" +
    ".chb .kp div{border:1px solid var(--ch-bd);border-radius:var(--ch-r);padding:10px 12px;min-width:0}.chb .kp span{font-size:12px;color:var(--ch-mf)}" +
    ".chb .kp b{display:block;font-size:17px;font-weight:700;margin-top:2px;direction:ltr;text-align:right;overflow-wrap:anywhere}" +
    ".chb .sw{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px;border:1px solid var(--ch-bd);border-radius:var(--ch-r);margin-bottom:14px}" +
    ".chb .sw>div{min-width:0}.chb .sw b{display:block;font-size:14px;font-weight:500;line-height:1.5}.chb .sw small{display:block;font-size:12.5px;color:var(--ch-mf);margin-top:2px;line-height:1.7}" +
    ".chb .tg{position:relative;width:42px;height:24px;border-radius:999px;background:var(--ch-mu);border:1px solid var(--ch-bd);cursor:pointer;flex:none;transition:background .2s}" +
    ".chb .tg::after{content:'';position:absolute;top:2px;right:2px;width:18px;height:18px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.3);transition:transform .2s}" +
    ".chb .tg.on{background:var(--ch-pr);border-color:transparent}.chb .tg.on::after{transform:translateX(-18px)}" +
    ".chb .two{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0 12px}" +
    ".chb .pw{position:relative}.chb .pw input{padding-left:40px;padding-right:12px}.chb .pw button{position:absolute;top:4px;left:4px;right:auto;width:28px;height:28px;border:0;background:transparent;color:var(--ch-mf);cursor:pointer;display:grid;place-items:center;border-radius:6px}.chb .pw button svg{width:16px;height:16px}" +
    ".chb .acts{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}.chb .acts .sp{flex:1}" +
    ".chb .note{margin-top:14px;font-size:12.5px;color:var(--ch-mf);line-height:1.9;border-top:1px dashed var(--ch-bd);padding-top:12px}" +
    ".chb .steps{list-style:none;margin:0;padding:0;counter-reset:st}.chb .steps li{counter-increment:st;position:relative;display:grid;grid-template-columns:30px minmax(0,1fr);column-gap:14px;padding:0 0 16px 0;min-height:44px}.chb .steps li>b,.chb .steps li>span{grid-column:2}.chb .steps li:last-child{padding-bottom:0}.chb .steps li::before{content:counter(st);grid-column:1;grid-row:1 / span 2;align-self:start;justify-self:start;width:30px;height:30px;border-radius:999px;display:flex;align-items:center;justify-content:center;line-height:1;font-size:13px;font-weight:700;background:var(--ch-mu);border:1px solid var(--ch-bd)}.chb .steps li b{display:block;font-size:14px;line-height:1.6}.chb .steps li>span{display:block;font-size:13px;color:var(--ch-mf);line-height:1.85;margin-top:2px}" +
    ".chb .fld label{line-height:1.5}.chb .kp b{line-height:1.4}.chb .kp span{display:block;line-height:1.5}";
  var TG_ICON = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.9 4.3 18.7 19.4c-.2 1.1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.4-5 9.1-8.2c.4-.4-.1-.6-.6-.2L6.2 13 1.4 11.5c-1-.3-1-1 .2-1.5L20.6 2.8c.9-.3 1.6.2 1.3 1.5Z"/></svg>';
  var botTimer = null;
  function botCard(parent) {
    bcss();
    var box = document.createElement("section"); box.id = "ch-bot"; box.className = "chx chb"; box.dir = DIR(); themeVars(box);
    box.innerHTML =
      '<div class="top"><div class="lg">' + TG_ICON + T('</div><div class="tt"><b>ربات فروش تلگرام</b><p>کاربر پلن را انتخاب می‌کند، مبلغ را کارت‌به‌کارت می‌کند و رسید را می‌فرستد. پس از تأیید شما، اشتراک به‌صورت خودکار ساخته و برای کاربر ارسال می‌شود.</p></div><span class="pill off" data-b="pill"><i></i><span>خاموش</span></span></div>') +
      T('<div class="kp"><div><span>فروش امروز</span><b data-k="sales_today">0</b></div><div><span>درآمد امروز (تومان)</span><b data-k="revenue_today">0</b></div><div><span>کل فروش</span><b data-k="sales">0</b></div><div><span>رسید در انتظار</span><b data-k="pending">0</b></div></div>') +
      T('<div class="sw"><div><b>فعال بودن ربات</b><small>در حالت خاموش، ربات به هیچ پیامی پاسخ نمی‌دهد.</small></div><button class="tg" type="button" role="switch" aria-checked="false" data-b="en"></button></div>') +
      T('<div class="two"><div class="fld"><label>توکن ربات</label><div class="pw"><input class="ltr" data-b="tok" type="password" autocomplete="off" spellcheck="false" placeholder="123456789:AA…"><button type="button" tabindex="-1" aria-label="نمایش">') + IC.eye + T('</button></div><div class="hint">از ربات <span class="ltr">@BotFather</span> دریافت کنید.</div></div>') +
      T('<div class="fld"><label>آیدی عددی مدیر</label><input class="ltr" data-b="adm" inputmode="numeric" autocomplete="off" spellcheck="false" placeholder="123456789"><div class="hint">از ربات <span class="ltr">@userinfobot</span> دریافت کنید. چند مدیر را با کاما از هم جدا کنید.</div></div></div>') +
      '<div class="err" data-b="err"></div>' +
      T('<div class="acts"><button class="btn pri" type="button" data-b="save">ذخیره</button><button class="btn" type="button" data-b="test">ارسال پیام آزمایشی</button><span class="sp"></span><a class="btn" data-b="open" target="_blank" rel="noopener" style="display:none">') + TG_ICON + T('<span>باز کردن ربات</span></a></div>') +
      T('<div class="note">منوی مدیریت ربات (دستور <span class="ltr">/admin</span>) شامل پلن‌ها و قیمت‌ها، اطلاعات پرداخت، مدیریت کاربران (افزایش و کاهش موجودی، پیام، مسدودسازی)، کیف پول و سیستم دعوت، کدهای تخفیف، اکانت تست رایگان، متن‌ها، کانال و عضویت اجباری، رسیدهای در انتظار، پیام همگانی، بکاپ کامل و باز و بسته کردن فروش است. یادآوری تمدید و بکاپ روزانه به‌صورت خودکار انجام می‌شوند.</div>');
    parent.appendChild(box);
    var $b = function (k) { return box.querySelector('[data-b="' + k + '"]'); }, en = $b("en"), tok = $b("tok"), adm = $b("adm"), err = $b("err");
    function setEn(v) { en.classList.toggle("on", v); en.setAttribute("aria-checked", v ? "true" : "false"); }
    en.onclick = function () { setEn(!en.classList.contains("on")); };
    box.querySelector(".pw button").onclick = function () { var show = tok.type === "password"; tok.type = show ? "text" : "password"; this.innerHTML = show ? IC.eyeoff : IC.eye; };
    function showErr(m) { err.textContent = m || ""; err.classList.toggle("on", !!m); }
    function paint(v, fill) {
      var pill = $b("pill"), cls = v.running ? "on" : (v.enabled && v.error ? "bad" : "off");
      pill.className = "pill " + cls; pill.lastChild.innerHTML = v.running ? T("آنلاین") + (v.username ? ' <span class="ltr">@' + esc(v.username) + "</span>" : "") : (v.enabled ? (v.error ? T("خطا در اتصال") : T("در حال اتصال…")) : T("خاموش"));
      if (v.enabled && v.error && !v.running) showErr(v.error);
      var s = v.stats || {};
      ["sales_today", "sales", "pending"].forEach(function (k) { box.querySelector('[data-k="' + k + '"]').textContent = s[k] || 0; });
      box.querySelector('[data-k="revenue_today"]').textContent = (s.revenue_today || 0).toLocaleString("en-US");
      var op = $b("open"); if (v.username) { op.href = "https://t.me/" + v.username; op.style.display = ""; } else op.style.display = "none";
      if (fill) { setEn(!!v.enabled); tok.value = v.token_mask || ""; adm.value = (v.admins || []).join(", "); }
    }
    function load(fill) { return post("/chost/bot", {}, findToken()).then(function (x) { if (x[0] === 200) paint(x[1], fill); }).catch(function () {}); }
    $b("save").onclick = function () {
      var b = this; showErr(""); b.disabled = true; b.textContent = "…";
      post("/chost/bot/save", { enabled: en.classList.contains("on"), token: tok.value.trim(), admins: adm.value }, findToken()).then(function (x) {
        b.disabled = false; b.textContent = T("ذخیره");
        if (x[0] !== 200) return showErr(x[1].detail || T("ذخیره نشد"));
        paint(x[1], true); toast(x[1].enabled ? T("تنظیمات ذخیره شد. ربات چند لحظه‌ی دیگر آنلاین می‌شود") : T("تنظیمات ذخیره شد. ربات خاموش است"));
        [1200, 2500, 4500, 8000, 14000].forEach(function (ms) { setTimeout(function () { if (document.body.contains(box)) load(false); }, ms); });
      }).catch(function () { b.disabled = false; b.textContent = T("ذخیره"); showErr(T("ارتباط با سرور برقرار نشد")); });
    };
    $b("test").onclick = function () {
      var b = this; showErr(""); b.disabled = true;
      post("/chost/bot/test", {}, findToken()).then(function (x) { b.disabled = false; if (x[0] !== 200) return showErr(x[1].detail || T("ارسال نشد")); toast(T("پیام آزمایشی برای ") + x[1].sent + T(" مدیر ارسال شد")); })
        .catch(function () { b.disabled = false; showErr(T("ارتباط با سرور برقرار نشد")); });
    };
    load(true);
    clearInterval(botTimer);
    botTimer = setInterval(function () { if (!document.body.contains(box)) { clearInterval(botTimer); return; } load(false); }, 15000);
  }


  /* ---------- 7) replace PasarGuard's "support / donate" popup with the panel creator card ---------- */
  var CREATOR = { name: "CHOST", channel: "CHOST543" };
  var DONATE_RE = /حمایت مالی|حمایت کنید|حمایت از ما|دونیت|کمک مالی|donat|support us|sponsor|buy me a coffee|crypto|tether|usdt/i;
  function closeNative(dlg) {
    try { dlg.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", code: "Escape", keyCode: 27, bubbles: true })); } catch (e) {}
    setTimeout(function () {
      if (!document.body.contains(dlg)) return;
      var root = dlg.parentElement; dlg.style.display = "none";
      if (root) Array.prototype.forEach.call(root.children, function (c) { if (c !== dlg && /fixed/.test(getComputedStyle(c).position) && !c.closest(".chx")) c.style.display = "none"; });
      document.body.style.pointerEvents = ""; document.body.style.overflow = ""; document.body.removeAttribute("data-scroll-locked");
    }, 250);
  }
  function creatorCard() {
    try { if (sessionStorage.getItem("ch-creator-shown")) return; sessionStorage.setItem("ch-creator-shown", "1"); } catch (e) {}
    var link = "https://t.me/" + CREATOR.channel;
    dialog({ cls: "chk", title: "", ok: TG_ICON + T("<span>عضویت در کانال</span>"), cancel: T("بستن"),
      html: '<div class="done" style="padding-top:4px"><div class="ok" style="background:linear-gradient(135deg,#f5dc9c,#a47c32);color:#0b0b0b;width:72px;height:72px;border-radius:20px">' +
        '<svg viewBox="0 0 32 32" style="width:38px;height:38px;stroke-dasharray:none;animation:none"><path d="M16 3C9.6 3 5.5 7.8 5.5 14v14l3.5-2.5 3.5 2.5 3.5-2.5 3.5 2.5 3.5-2.5 3.5 2.5V14C26.5 7.8 22.4 3 16 3Z" fill="#0b0b0b"/><path d="M10.5 14.5c.8-1.3 2.6-1.3 3.4 0M18.1 14.5c.8-1.3 2.6-1.3 3.4 0" stroke="#f5dc9c" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg></div>' +
        T('<b>سازنده‌ی پنل: <span class="ltr" style="letter-spacing:3px"></span></b><p>این پنل اختصاصی توسط <b class="ltr" style="display:inline;font-size:inherit"></b> ساخته و پشتیبانی می‌شود.<br>برای اطلاع از آپدیت‌ها، آموزش‌ها و پشتیبانی، عضو کانال رسمی شوید.</p>') +
        '<p style="margin-top:12px"><a class="ltr" target="_blank" rel="noopener" style="font-weight:700;color:inherit;text-decoration:none;padding:6px 14px;border:1px solid var(--ch-bd);border-radius:999px;display:inline-block"></a></p></div>',
      onOpen: function (d) {
        d.root.querySelector("h2").style.display = "none";
        var spans = d.root.querySelectorAll(".done .ltr"); spans[0].textContent = CREATOR.name; spans[1].textContent = CREATOR.name;
        var a = d.root.querySelector(".done a"); a.href = link; a.textContent = "@" + CREATOR.channel;
      },
      onOk: function () { window.open(link, "_blank", "noopener"); return true; } });
  }
  function isForm(d) {
    if (d.querySelector("textarea, select, [role=combobox]")) return true;
    var ins = d.querySelectorAll("input");
    for (var i = 0; i < ins.length; i++) { var t = String(ins[i].getAttribute("type") || "text").toLowerCase(); if (t !== "checkbox" && t !== "radio" && t !== "hidden") return true; }
    return false;
  }
  function killDonate() {
    var ds = document.querySelectorAll('[role="dialog"], [role="alertdialog"]');
    for (var i = 0; i < ds.length; i++) {
      var d = ds[i]; if (d.closest(".chx") || d.getAttribute("data-ch-killed")) continue;
      if (isForm(d)) continue;   /* real panel forms (create / edit user...) are never touched */
      if (DONATE_RE.test(d.textContent || "")) { d.setAttribute("data-ch-killed", "1"); closeNative(d); if (findToken()) setTimeout(creatorCard, 350); }
    }
  }
  var creatorQueued = false;
  function nativeDialogOpen() {
    var ds = document.querySelectorAll('[role="dialog"], [role="alertdialog"], [data-state="open"][data-slot="sheet-content"]');
    for (var i = 0; i < ds.length; i++) if (!(ds[i].closest && ds[i].closest(".chx")) && !ds[i].getAttribute("data-ch-killed") && ds[i].style.display !== "none") return true;
    return false;
  }
  function creatorKey() { var t = findToken() || ""; return "ch-creator-" + t.slice(-24); }
  function greet() {   /* once per login, only when nothing else is open; it never blocks the panel */
    var cd = document.querySelector(".chd .dl.chk"), card = cd && cd.closest(".chd");
    if (card && nativeDialogOpen()) { if (card.parentNode) card.parentNode.removeChild(card); document.body.style.overflow = ""; }
    if (creatorQueued || !findToken() || !document.querySelector('[data-sidebar="sidebar"], aside')) return;
    try { if (localStorage.getItem(creatorKey()) || sessionStorage.getItem("ch-creator-shown")) return; } catch (e) { return; }
    creatorQueued = true;
    setTimeout(function () { creatorQueued = false;
      if (document.querySelector(".chd") || nativeDialogOpen() || PAGE) return;
      try { localStorage.setItem(creatorKey(), "1"); } catch (e) {}
      creatorCard(); }, 1500);
  }

  /* ---------- run + keep up with page changes ---------- */
  var queued = false;
  function brand() { if (document.title.indexOf("CHOST") !== 0) document.title = "CHOST Panel"; }
  var lastLang = null;
  function langWatch() {
    _lg.t = 0; var l = LANG(); if (l === lastLang) return; var first = lastLang === null; lastLang = l; if (first) return;
    var reopen = PAGE ? PAGE.key : null;
    Array.prototype.forEach.call(document.querySelectorAll("[data-ch]"), function (it) { if (it.parentNode) it.parentNode.removeChild(it); });
    var ol = document.getElementById("ch-own-link"); if (ol && ol.parentNode) ol.parentNode.removeChild(ol);
    if (reopen) { closePage(false, false, true); mountPages(); openPage(reopen); }
  }
  var STEPS = [langWatch, brand, killDonate, greet, whoAmI, sweep, mountPages, mountOwner];
  function tick() { for (var i = 0; i < STEPS.length; i++) { try { STEPS[i](); } catch (e) { /* one step failing never stops the others or the panel */ } } }
  function schedule() { if (queued) return; queued = true; requestAnimationFrame(function () { queued = false; tick(); }); }
  function start() { tick(); new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true, characterData: true }); setInterval(schedule, 2000); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
