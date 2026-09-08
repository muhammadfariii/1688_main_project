# 1688 Sourcing & Factory Intelligence Tool
### Client Overview, Costing Breakdown & Project Guide
*Prepared for non-technical stakeholders, business owners, and sourcing teams.*

---

## 1. Complete API Cost Breakdown

The application connects to live 1688 data via cloud scraping infrastructure on [Apify](https://apify.com/). The pricing is structured to be transparent, predictable, and starts with a permanent free monthly tier.

### Part A: The Free Tier ($0.00 / Month)
* **Monthly Free Credits:** Every Apify account receives **$5.00 in free usage credits every month** automatically. This renews each month and never expires.
* **No Credit Card Required:** You can create an account and test live 1688 data without entering any payment card details.
* **Cost Per Action:**
  * **Starting a Search Run:** Fixed fee of **$0.004** per search query (less than half a cent).
  * **Extracting Supplier Leads:** Billed at **$0.45 per 1,000 verified supplier leads** ($0.00045 per lead).
* **What You Get for Free:**
  * With your $5.00 monthly free allowance, you can extract between **10,000 and 11,000 verified factory leads every month completely free**.
  * For most small-to-medium businesses conducting regular product research, the free tier is sufficient to cover ongoing operations without spending anything.

---

### Part B: What Happens If You Exceed the Free Tier?

If your sourcing needs expand and you extract more than 10,000 suppliers in a single month, you only pay for the exact volume you use on a pay-as-you-go basis.

#### Monthly Usage Scenarios & Actual Costs

| Sourcing Volume Level | Monthly Supplier Leads | Gross Data Cost | Minus $5 Free Allowance | Total Cost to You |
| :--- | :---: | :---: | :---: | :---: |
| **Standard Research** | Up to 10,000 leads | $4.50 | -$5.00 | **$0.00 (FREE)** |
| **Active Sourcing Campaign** | 25,000 leads | $11.25 | -$5.00 | **$6.25 / month** |
| **Broad Catalog Sourcing** | 50,000 leads | $22.50 | -$5.00 | **$17.50 / month** |
| **High-Volume / Agency** | 100,000 leads | $45.00 | -$5.00 | **$40.00 / month** |

*Note: There are no monthly maintenance charges or lock-in contracts. You only pay for successful rows written to your dataset.*

---

### Part C: Safety & Budget Controls (No Surprise Bills)
* **Budget Caps:** You can set a monthly spending limit inside your Apify account (for example, setting a hard stop at $10.00 or $20.00).
* **Auto-Pause:** If your usage ever reaches that limit, searches pause automatically until the next month, ensuring you never incur unexpected charges.

---

## 2. Project Explanation in Plain English

### The Business Challenge
When sourcing products from China, most Western businesses look on **Alibaba.com**. However, Alibaba.com is an English-language export platform where export agents and middlemen mark up prices by **30% to 50%**.

The real domestic prices are on **1688.com** (Alibaba's internal wholesale marketplace for Chinese factories). However, buying on 1688 presents major hurdles:
1. It is entirely in Chinese.
2. It blocks international users behind QR-code login walls.
3. Thousands of trading middlemen pose as "factories" to take a cut.
4. If you have a collection of 5 to 10 products, sourcing them from separate vendors triples your shipping, inspection, and communication headaches.

---

### How This Sourcing Tool Solves the Problem

1. **Automated Factory vs. Middleman Detection:**
   * The tool's AI classifier evaluates every seller's official Chinese corporate name, plant facility area (m²), employee numbers, and official Alibaba on-site factory inspection badges (such as *Super Factory* and *Deep Audited*).
   * It labels each vendor as a **Factory** or **Trading Company** with a clear confidence score (e.g., *98% Factory Confidence*), keeping middlemen off your shortlist.

2. **Configurable Scraping Depth (Pages UI Selector):**
   * A dedicated **"Pages to Fetch"** control right in the search bar lets you decide how deep to search:
     * **1 Page (~20 items):** Fast, lowest cost, and focuses on the most relevant, top-selling suppliers.
     * **2–3 Pages (~40–60 items):** Deeper discovery to uncover specialized or smaller workshops.
     * **5–10 Pages (~100–200 items):** Broad sweep for comprehensive industry research.
   * You can also set your preferred default depth in the **Config Modal**, and the tool remembers your choice across sessions.

3. **Multi-Product Consolidation (One-Stop Manufacturing):**
   * Instead of managing multiple suppliers for separate items (e.g., water bottles, mugs, and silicone lids), paste your entire product line into the **Multiple Products** tab.
   * The tool identifies which single factory can produce all or most of your catalog under one roof, saving thousands in freight and consolidated orders.

4. **Direct Contact Information & Clean Links:**
   * **Phone & Mobile Numbers:** Surfaces direct telephone numbers and sales manager contacts.
   * **1688 Official Contact Page:** 1-click link to the vendor's verified government business license and legal address.
   * **1-Click AliWangWang Chat:** Direct button opening an instant chat window with the factory on 1688's messenger.
   * **Direct Product Links:** Canonical product links plus a **Mobile View** option that opens immediately in any browser without desktop login popups.

5. **One-Click Excel & CSV Export:**
   * Downloads clean, formatted spreadsheets with working clickable hyperlinks, ready to hand off to freight forwarders, sourcing agents, or your executive team.

6. **Built-in Offline Demo Mode:**
   * Includes a toggle at the top of the interface. Anyone can test all features and export reports instantly with realistic mock data without needing an API key or internet setup.

---

## 3. Quick-Start Guide (How to Use the Tool)

1. **Launch the Application:** Open the web tool in your browser (`http://localhost:8000` or your hosted URL).
2. **Select Scraping Depth:** In the **Pages to Fetch** dropdown, pick your desired search depth (1 page recommended for quick checks, 2–3 for deep scans).
3. **Single Product Search:** Enter any product keyword (in English or Chinese). Review the ranked list of verified factories, pricing in RMB, and direct phone/chat buttons.
4. **Multi-Product Sourcing:** Click the **Multiple Products** tab, paste a list of items (one per line), and click **Find Suppliers by Coverage**. The tool calculates which supplier covers the largest percentage of your items.
5. **Export Your Report:** Click **Export Excel (.xlsx)** to download a complete spreadsheet containing all product URLs, contact phone numbers, and factory credentials.
