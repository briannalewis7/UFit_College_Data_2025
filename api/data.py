import requests
from bs4 import BeautifulSoup
import re

class Constants:
    ACT = 1
    SAT = 2
    BOTH = 3

# School name mappings
SCHOOL_NAME_MAP = {
    "ucla": "University of California Los Angeles",
    "uclosangeles": "University of California Los Angeles",
    "ucb": "University of California Berkeley",
    "ucberkeley": "University of California Berkeley",
    "berkeley": "University of California Berkeley",
    "ucsb": "University of California Santa Barbara",
    "ucsantabarbara": "University of California Santa Barbara",
    "ucsd": "University of California San Diego",
    "ucsandiego": "University of California San Diego",
    "uci": "University of California Irvine",
    "ucirvine": "University of California Irvine",
    "ucd": "University of California Davis",
    "ucdavis": "University of California Davis",
    "ucsc": "University of California Santa Cruz",
    "ucsantacruz": "University of California Santa Cruz",
    "ucr": "University of California Riverside",
    "ucriverside": "University of California Riverside",
    "ucm": "University of California Merced",
    "ucmerced": "University of California Merced",
    "mizzou": "University of Missouri Columbia",
    "unversityofmissouri": "University of Missouri Columbia",
    "mit": "Massachusetts Institute of Technology",
    "caltech": "California Institute of Technology",
    "nyu": "New York University",
    "usc": "University of Southern California",
    "upenn": "University of Pennsylvania",
    "penn": "University of Pennsylvania",
    "pennstate": "Penn State University Park",
    "psu": "Penn State University Park",
    "upitt": "University of Pittsburgh",
    "pitt": "University of Pittsburgh",
    "washu": "Washington University in St. Louis",
    "wustl": "Washington University in St. Louis",
    "uva": "University of Virginia",
    "umich": "University of Michigan",
    "umichigan": "University of Michigan",
    "michigan": "University of Michigan",
    "umass": "University of Massachusetts Amherst",
    "universityofmassachusetts": "University of Massachusetts Amherst",
    "indiana": "Indiana University Bloomington",
    "iu": "Indiana University Bloomington",
    "iowa": "University of Iowa",
    "unc": "University of North Carolina at Chapel Hill",
    "universityofnorthcarolina": "University of North Carolina at Chapel Hill",
    "uchicago": "University of Chicago",
    "chicago": "University of Chicago",
    "gt": "Georgia Institute of Technology",
    "georgiatech": "Georgia Institute of Technology",
    "uga": "University of Georgia",
    "smu": "Southern Methodist University",
    "uiuc": "University of Illinois at Urbana-Champaign",
    "illinois": "University of Illinois at Urbana-Champaign",
    "universityofillinois": "University of Illinois at Urbana-Champaign",
    "uofi": "University of Illinois at Urbana-Champaign",
    "utaustin": "University of Texas at Austin",
    "universityoftexas": "University of Texas at Austin",
    "austin": "University of Texas at Austin",
    "texas": "University of Texas at Austin",
    "tcu": "Texas Christian University",
    "texaschristian": "Texas Christian University",
    "uw": "University of Washington",
    "uwashington": "University of Washington",
    "cwru": "Case Western Reserve University",
    "casewestern": "Case Western Reserve University",
    "uwmadison": "University of Wisconsin Madison",
    "wisconsin": "University of Wisconsin Madison",
    "madison": "University of Wisconsin Madison",
    "universityofwisconsin": "University of Wisconsin Madison",
    "minnesota": "University of Minnesota Twin Cities",
    "universityofminnesota": "University of Minnesota Twin Cities",
    "minn": "University of Minnesota Twin Cities",
    "virginiatech": "Virginia Polytechnic Institute and State University",
    "vatech": "Virginia Polytechnic Institute and State University",
    "loyola": "Loyola University Chicago",
    "mohio": "Miami University",
    "miamiohio": "Miami University",
    "miamiofohio": "Miami University",
    "miamiu": "Miami University",
    "umiami": "University of Miami",
    "miamiflorida": "University of Miami",
    "umiami": "University of Miami",
    "osu": "Ohio State University",
    "theohiostate": "Ohio State University",
    "msu": "Michigan State University",
    "uofsc": "University of South Carolina",
    "gwu": "George Washington University",
    "gw": "George Washington University",
    "boulder": "University of Colorado Boulder",
    "colorado": "University of Colorado Boulder",
    "cuboulder": "University of Colorado Boulder",
    "coloradocollege": "Colorado College",
    "costate": "Colorado State University",
    "iowastate": "Iowa State University",
    "tulane": "Tulane University",
    "isu": "Illinois State University",
    "duke": "Duke University",
    "northwestern": "Northwestern University",
    "northeastern": "Northeastern University",
    "jhu": "Johns Hopkins University",
    "vanderbilt": "Vanderbilt University",
    "cmu": "Carnegie Mellon University",
    "notredame": "University of Notre Dame",
    "emory": "Emory University",
    "georgetown": "Georgetown University",
    "uf": "University of Florida",
    "bu": "Boston University",
    "bc": "Boston College",
    "tufts": "Tufts University",
    "rutgers": "Rutgers The State University of New Jersey",
    "umd": "University of Maryland College Park",
    "lehigh": "Lehigh University",
    "purdue": "Purdue University",
    "rochester": "University of Rochester",
    "floraidastate": "Florida State University",
    "fsu": "Florida State University",
    "texasa&m": "Texas A&M University",
    "wakeforest": "Wake Forest University",
    "williamandmary": "College of William and Mary",
    "rice": "Rice University",
    "columbia": "Columbia University",
    "dartmouth": "Darthmouth College",
    "brown": "Brown University",
    "cornell": "Cornell University",
    "yale": "Yale University",
    "stanford": "Stanford University",
    "harvard": "Harvard University",
    "princeton": "Princeton University",
    "uic": "University of Illinois at Chicago",
    "asu" : "Arizona State University",
    "tennessee": "The University of Tennessee at Knoxville",
    "oklahomastate": "Oklahoma State University Stillwater",
    "texasamuniversity" : "Texas A M University"
}


def normalize_school_name(name):
    """Convert user input to the official school name"""
    name_lower = name.strip().lower().replace(" ", "").replace("-", "").replace("&", "")
    return SCHOOL_NAME_MAP.get(name_lower, name.strip())


class Extractor():
    def __init__(self, school_name: str):
        # Normalize the name first using the mapping
        self.original_name = school_name.strip()
        self.name = normalize_school_name(self.original_name).title()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self._error_logged = False
        # Try to find a valid URL
        self.name, self.name_url, self.base_url = self._find_valid_url()

    def _find_valid_url(self):
        """Try different URL patterns to find a valid school page"""
        # Try the normalized name first
        name_url = self.name.lower().replace(" ", "-").replace(".", "")
        base_url = f"https://waf.collegedata.com/college-search/{name_url}"
        
        if self._check_url_valid(base_url):
            return self.name, name_url, base_url
        
        # Try adding "university" at the end
        name_with_univ = f"{self.name} University"
        name_url = name_with_univ.lower().replace(" ", "-").replace(".", "")
        base_url = f"https://waf.collegedata.com/college-search/{name_url}"
        
        if self._check_url_valid(base_url):
            return name_with_univ, name_url, base_url
        
        # Try adding "University of" at the beginning
        name_univ_of = f"University of {self.name}"
        name_url = name_univ_of.lower().replace(" ", "-").replace(".", "")
        base_url = f"https://waf.collegedata.com/college-search/{name_url}"
        
        if self._check_url_valid(base_url):
            return name_univ_of, name_url, base_url
        
        # Try "[Name] College"
        name_with_college = f"{self.name} College"
        name_url = name_with_college.lower().replace(" ", "-").replace(".", "")
        base_url = f"https://waf.collegedata.com/college-search/{name_url}"
        
        if self._check_url_valid(base_url):
            return name_with_college, name_url, base_url
        
        # If nothing works, return the original
        name_url = self.name.lower().replace(" ", "-").replace(".", "")
        base_url = f"https://waf.collegedata.com/college-search/{name_url}"
        return self.name, name_url, base_url
    
    def _check_url_valid(self, url):
        """Check if a URL returns a valid response without creating soup"""
        try:
            r = requests.get(url, headers=self.headers, timeout=5)
            return r.status_code == 200
        except:
            return False

    def get_full_data(self, test_pref):
        # Test if base URL exists first
        soup = self._get_soup(self.base_url)
        if soup is None:
            return None  # School not found, skip entirely

        data = {"University": self.name}
        data["Location"] = self.get_location()
        data["Number of Undergraduates"] = self.get_undergrad_count()

        # Admission data
        data["Test Policy"] = self.get_test_policy()
        data["Avg GPA"] = self.get_avg_gpa()

        if test_pref == Constants.ACT:
            data["ACT Range"] = self.get_act_range()
        elif test_pref == Constants.SAT:
            data["SAT Range"] = self.get_sat_range()
        else:
            data["SAT Range"] = self.get_sat_range()
            data["ACT Range"] = self.get_act_range()

        data["Acceptance Rate"] = self.get_acceptance_rate()
        
        # Money data
        data["Cost of Attendance"] = self.get_total_cost()
        data["Merit Aid"] = self.get_merit_aid_no_need()
        data["Likely/Target/Reach"] = " " #placeholder
        data["ED/EA/Rolling"] = self.get_early_options()
        data["Application Deadlines"] = self.get_application_deadlines()
        return data

    # === ADMISSION PAGE EXTRACTORS ===
    
    def get_test_policy(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        if soup: 
            test_policy = self._get_div_value(soup, "SAT or ACT")
            if test_policy.strip().lower() == "considered if submitted":
                return "optional"
            else:
                return test_policy
        else:
            return "N/A"
    
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
        return rate.strip().split("%")[0] + "%" if rate else "N/A"
    
    def get_early_decision(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        return self._get_div_value(soup, "Early Decision Offered") if soup else "N/A"
    
    def get_early_action(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        return self._get_div_value(soup, "Early Action Offered") if soup else "N/A"
    
    def get_early_options(self):
        ea = self.get_early_action().strip()
        ed = self.get_early_decision().strip()
        if ea.strip() == "N/A" and ed.strip() == "N/A":
            return "N/A"
        elif ea != "No" and ed != "No":
            return "ED, EA"
        elif ea != "No":
            return "EA"
        elif ed != "No":
            return "ED"
        elif self.get_rolling():
             return "Rolling"
        else:
            return "RD only"

    def get_rolling(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        if soup: 
            reg = self._get_div_value(soup, "Regular Admission Deadline")
            if reg.strip() == "Rolling":
                return True
            else: 
                return False
        else: return False

    def get_total_cost(self):
        soup = self._get_soup(f"{self.base_url}")
        if not soup:
            return "N/A"
        else:
            if self._get_div_value(soup, "In-state:") != "N/A": #means public school
                if "Illinois" in self.name.split():
                    return self._get_div_value(soup, "Cost of Attendance").replace("In-state: ", "")
                else:
                    return self._get_div_value(soup, "In-state:").replace("Out-of-state: ", "")
            else:
                return self._get_div_value(soup, "Cost of Attendance")

        
    # === MONEY MATTERS PAGE EXTRACTORS ===
    
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
                text = re.sub(r"^\S+\s*", "", text)
                text = text.replace("(", "").replace(")", "").replace("of freshmen had no financial need and ", "").replace("merit aid, average amount ", "")
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

    def get_application_deadlines(self):
        soup = self._get_soup(f"{self.base_url}/admission")
        if soup:
            deadlines = {}
            if self.get_early_decision() not in ["N/A", "No"]:
                deadlines["ED"] = self._get_div_value(soup, "Early Decision Deadline")
            if self.get_early_action() not in ["N/A", "No"]:
                deadlines["EA"] = self._get_div_value(soup, "Early Action Deadline")
            deadlines["RD"] = self._get_div_value(soup, "Regular Admission Deadline")
            string = ""
            for key in deadlines:
                deadline = deadlines[key].split(', ')
                deadline = deadline[0]
                string += f"{key}: {deadline}, "
            return string[:len(string)-2]
        else:
            return "N/A"


 
    # === HELPER METHODS ===

    def _get_soup(self, url):
        try:
            r = requests.get(url, headers=self.headers)
            if r.status_code == 200:
                return BeautifulSoup(r.text, 'html.parser')
            else:
                self._url_error_handling(url, r.status_code)
                return None
        except Exception as e:
            self._url_error_handling(url, error=str(e))
            return None

    def _url_error_handling(self, url, status_code=None, error=None):
        """Handle URL errors and notify user"""
        # Only print error message once per school (for the base URL)
        if url == self.base_url and not self._error_logged:
            if status_code:
                print(f"  ⚠ Warning: Unable to find data for '{self.name}' (Status: {status_code})")
            else:
                print(f"  ⚠ Warning: Unable to find data for '{self.name}' (Error: {error})")
            print(f"  → Skipping this school\n")
            self._error_logged = True  # Mark that we've logged the error

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