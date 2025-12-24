import requests
from bs4 import BeautifulSoup
import re
import csv

class Extractor():
    def __init__(self, school_name: str):
        self.name = school_name
        self.name_url = self.name.strip().lower().replace(" ", "-").replace(".", "")
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.base_url = f"https://waf.collegedata.com/college-search/{self.name_url}"

    def get_full_data(self):
        data = {"University": self.name}
        data["Location"] = self.get_location()
        data["Number of Undergraduates"] = self.get_undergrad_count()

        # Admission data
        data["Test Policy"] = self.get_test_policy()
        data["SAT Range"] = self.get_sat_range()
        data["ACT Range"] = self.get_act_range()
        data["Avg GPA"] = self.get_avg_gpa()
        data["Acceptance Rate"] = self.get_acceptance_rate()
        data["Early Decision"] = self.get_early_decision()
        data["Early Action"] = self.get_early_action()
        
        # Money data
        data["Cost (Total)"] = self.get_total_cost()
        data["Merit Aid"] = self.get_merit_aid_no_need()

        return data

    # === ADMISSION PAGE EXTRACTORS ===
    
    def get_test_policy(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        return self._get_div_value(soup, "SAT or ACT") if soup else "N/A"
    
    def get_sat_range(self):
        soup = self._get_soup(f"{self.base_url}")
        if not soup:
            return "N/A"
        
        # Extract SAT Math range
        math_range = self._get_sat_section_range(soup, "SAT Math")
        ebrw_range = self._get_sat_section_range(soup, "SAT EBRW")
        
        if math_range == "N/A" or ebrw_range == "N/A":
            return "N/A"
        
        # Parse the ranges (e.g., "770-800" -> (770, 800))
        math_match = re.search(r'(\d+)-(\d+)', math_range)
        ebrw_match = re.search(r'(\d+)-(\d+)', ebrw_range)
        
        if not math_match or not ebrw_match:
            return "N/A"
        
        # Calculate composite range
        math_low, math_high = int(math_match.group(1)), int(math_match.group(2))
        ebrw_low, ebrw_high = int(ebrw_match.group(1)), int(ebrw_match.group(2))
        
        composite_low = math_low + ebrw_low
        composite_high = math_high + ebrw_high
        
        return f"{composite_low}-{composite_high}"

    def _get_sat_section_range(self, soup, section_name):
        """Helper to extract SAT Math or SAT EBRW range"""
        label_div = soup.find('div', string=re.compile(f"^{section_name}$", re.I))
        if not label_div:
            return "N/A"
        
        # Look through sibling divs for the range
        current = label_div.find_next_sibling('div')
        while current:
            text = current.get_text(strip=True)
            if 'range of middle 50%' in text.lower():
                match = re.search(r'(\d+)-(\d+)', text)
                return match.group(0) if match else "N/A"
            current = current.find_next_sibling('div')
        
        return "N/A"
    
    def get_act_range(self):
        soup = self._get_soup(f"{self.base_url}")
        if not soup:
            return "N/A"
        
        # Find the ACT Composite label
        label_div = soup.find('div', string=re.compile(r"ACT Composite", re.I))
        if not label_div:
            return "N/A"
        
        # Look through all sibling divs to find the one with "range of middle 50%"
        current = label_div.find_next_sibling('div')
        while current:
            text = current.get_text(strip=True)
            if 'range of middle 50%' in text.lower():
                # Extract just the range numbers (e.g., "33-35")
                match = re.search(r'(\d+)-(\d+)', text)
                return match.group(0) if match else text
            current = current.find_next_sibling('div')
        
        return "N/A"
    
    def get_avg_gpa(self):
        soup = self._get_soup(f"{self.base_url}")
        return self._get_div_value(soup, "Average GPA") if soup else "N/A"
    
    def get_acceptance_rate(self):
        soup = self._get_soup(f"{self.base_url}")
        if not soup:
            return "N/A"
        rate = soup.find(string=re.compile(r'applicants were admitted', re.I))
        return rate.strip() if rate else "N/A"
    
    def get_early_decision(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        return self._get_div_value(soup, "Early Decision Offered") if soup else "N/A"
    
    def get_early_action(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        return self._get_div_value(soup, "Early Action Offered") if soup else "N/A"

    # === MONEY MATTERS PAGE EXTRACTORS ===
    
    def get_total_cost(self):
        soup = self._get_soup(f"{self.base_url}/money-matters")
        if not soup:
            return "N/A"
        
        t_fees = self._get_div_value(soup, "Tuition & Fees")
        r_board = self._get_div_value(soup, "Room & Board")
        
        if t_fees == "N/A" or r_board == "N/A":
            return "N/A"
        
        try:
            tuition_amt = int(t_fees.replace(',', "").replace('$', ""))
            room_amt = int(r_board.replace(',', "").replace('$', ""))
            total = tuition_amt + room_amt
            return f"{t_fees} (T) + {r_board} (R&B) = ${total:,}"
        except:
            return f"{t_fees} (T) + {r_board} (R&B)"
    
    def get_merit_aid_no_need(self):
        soup = self._get_soup(f"{self.base_url}/money-matters")
        if not soup:
            return "N/A"
        
        # Find the "Merit-Based Gift" label
        label_div = soup.find('div', string=re.compile(r'Merit-Based Gift', re.I))
        if not label_div:
            return "N/A"
        
        # Look through sibling divs for the one about "no financial need"
        current = label_div.find_next_sibling('div')
        while current:
            text = current.get_text(strip=True)
            if 'no financial need' in text.lower() and 'merit aid' in text.lower():
                return text
            current = current.find_next_sibling('div')
        
        return "N/A"
    
    def get_undergrad_count(self):
        soup = self._get_soup(f"{self.base_url}/students")
        if not soup:
            return "N/A"
        
        # Look for "All Undergraduates" label
        label_div = soup.find('div', string=re.compile(r'All Undergraduates', re.I))
        if not label_div:
            return "N/A"
        
        # Get the next sibling div which contains the value
        value_div = label_div.find_next_sibling('div')
        if value_div:
            return value_div.get_text(strip=True)
        
        return "N/A"
    
    def get_location(self):
        soup = self._get_soup(f"{self.base_url}/campus-life")
        if not soup:
            return "N/A"
        
        # Look for Location in StatLine structure
        label_div = soup.find('div', class_=re.compile(r'StatLine_label'), string=re.compile(r'Location', re.I))
        if not label_div:
            # Fallback to TitleValue structure
            return self._get_div_value(soup, "Location")
        
        # Get the next sibling div with StatLine_value class
        value_div = label_div.find_next_sibling('div', class_=re.compile(r'StatLine_value'))
        if value_div:
            return value_div.get_text(strip=True)
        
        return "N/A"

    # === HELPER METHODS ===

    def _get_soup(self, url):
        try:
            r = requests.get(url, headers=self.headers)
            return BeautifulSoup(r.text, 'html.parser') if r.status_code == 200 else None
        except:
            return None

    def _get_div_value(self, soup, label_text):
        """
        Targeting the specific div structure:
        <div class="TitleValue_title...">Label</div>
        <div class="TitleValue_value...">Value</div>
        """
        label_div = soup.find('div', string=re.compile(f"^{label_text}$", re.I))
        
        if not label_div:
            label_div = soup.find('div', string=re.compile(label_text, re.I))
            
        if label_div:
            value_div = label_div.find_next_sibling('div')
            if value_div:
                return value_div.get_text(strip=True)
        
        # Fallback for table-based layouts
        target = soup.find(['td', 'th'], string=re.compile(label_text, re.I))
        if target:
            sibling = target.find_next_sibling('td')
            if sibling:
                return sibling.get_text(strip=True)
            
        return "N/A"

def main():
    user_input = input("Enter full school name. Please separate each school with a comma. \n")
    schools = user_input.split(",")
    # Collect all data
    all_results = []
    for school in schools:
        print(f"\nFetching data for: {school}...")
        ex = Extractor(school)
        results = ex.get_full_data()
        all_results.append(results)
        
        # Print to console
        for k, v in results.items():
            print(f"  {k}: {v}")
    
    # Write to CSV
    if all_results:
        filename = "college_data.csv"
        fieldnames = all_results[0].keys()  # Get column names from first result
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\n✓ Data saved to {filename}")

if __name__ == "__main__":
    main()