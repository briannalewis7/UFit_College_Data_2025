from data import Extractor
import csv

def export_file(all_results):
    name_input = input("Please enter name for output file: \n")
    if len(name_input) <= 0: 
        raise ValueError
    filename = name_input.strip() + ".csv"
    fieldnames = all_results[0].keys()  # Get column names from first result
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n✓ Data saved to {filename}")
    success = True
    return filename, success

def to_csv(all_results): 
    # Write to CSV  
    if all_results:
        success = False
        while not success:
            try: 
                filename, success = export_file(all_results)
            except ValueError: 
                print(f"\n Error saving output. Please enter valid file name.")
            except OSError as e:
                print(f"\n Error saving data. {e} Please make sure to only include valid characters in file name.\n")
    else:
        print("\nNo data collected - no CSV file created.")

def get_data(user_input):
    schools = [school.strip() for school in user_input.split(",")]  
    skipped = []
    # Collect all data
    all_results = []
    for school in schools:
        ex = Extractor(school)
        print(f"\nFetching data for: {ex.name}...")
        results = ex.get_full_data()
        
        if results is None:
            # School not found, skip it
            skipped.append(school)
            continue
            
        all_results.append(results)
        
        # Print to console
        for k, v in results.items():
            print(f"  {k}: {v}")

    if len(skipped) > 0: 
        skipped_string = "\n\n Unable to find data for: "
        for school in skipped:
            skipped_string += f"{school.title()}, "
        print(skipped_string.strip()[:-1])
    return all_results

def main():
    user_input = input("Enter full school name. Please separate each school with a comma. \n")
    all_results = get_data(user_input)
    done = False
    while not done:
        more_schools = input("\n Would you like to add more schools (y/n)? ")
        if more_schools.strip() in ["y", "yes"]:
            user_input2 = input(f"\nPlease enter school names, separated by a comma.\n")
            all_results.extend(get_data(user_input2))
        else:
            done = True


    #export to csv
    to_csv(all_results)

if __name__ == "__main__":
    main()