class ExtractData:
    def get_case_info(case_rows):
        # Initialize an empty dictionary to store the information
        info_dict = {}

        # get the case info in the 1st and 3rd rows
        case_info = []
        for row in case_rows:
            # get the rows in the tbody of table in the row
            tbody = row.find_element(By.TAG_NAME, "tbody")
            tbody_rows = tbody.find_elements(By.TAG_NAME, "tr")

            # Find all the div elements inside the tr element
            labels = driver.find_elements_by_xpath('//tr//div[@id="fontBold"]')
            values = driver.find_elements_by_xpath('//tr//td[2]')

            # Iterate through the elements and extract the text content
            for label, value in zip(labels, values):
                label_text = label.text.strip(':')  # Remove the trailing colon
                value_text = value.text.strip()
                info_dict[label_text] = value_text

        # save the case info in the dataframe using concat
        case_info_df = pd.DataFrame([info_dict])

        return case_info_df

    def get_cases(driver):
        # get the table with class nameList and id count
        case_table = driver.find_element_by_xpath("//table[@class='nameList' and @id='count']")

        # Get the case info table rows html
        case_info_table_rows_html = []
        for row in case_info_table_rows:
            case_info_table_rows_html.append(row.prettify())

        # save the file
        with open("case_info_table_rows.html", "w") as file:
            file.write(str(case_info_table_rows_html))

        # Get the page source
        page_source = driver.page_source

        # Create a BeautifulSoup object
        soup = BeautifulSoup(page_source, 'html.parser')

        # get the tr with id = "BackgroundWhite"
        background_white_tr = soup.find("tr", {"id": "BackgroundWhite"})

        # save the html of the tr
        background_white_tr_html = background_white_tr.prettify()

        # save the file
        with open("background_white_tr.html", "w") as file:
            file.write(background_white_tr_html)