

def extract_employee_years(extracted_review):
    employee_years_elements = extracted_review.select("div.cell.reviewBodyCell p.tightBot")
    if(len(employee_years_elements)>=1):
        employee_years =employee_years_elements[0].text
        employee_years = employee_years.split('(')
        if(len(employee_years)>1):
            return employee_years[1][:1]
        else:
            return 'not mentioned'
    else:
        return 'not mentioned'

def extract_recomends(extracted_review):
    recomends_dictionary_results = {}
    recommends_elements = extracted_review.select('div.recommends div.middle')
    for recommends_element in recommends_elements:
        is_recommended_element = recommends_element.select('.cell')[1].text.find('Recommends')>-1
        is_outlook_element = recommends_element.select('.cell')[1].text.find('Outlook')>-1
        is_approved_ceo_element = recommends_element.select('.cell')[1].text.find('CEO')>-1
        if(is_recommended_element):
            try:
                recomends_dictionary_results['recommends'] = recommends_element.select('i.sqLed')[0].attrs['class'].index('green')>0
            except ValueError:
                recomends_dictionary_results['recommends'] = False
        if(is_outlook_element):
            try:
                recomends_dictionary_results['positive_outlook'] = recommends_element.select('i.sqLed')[0].attrs['class'].index('green')>0
            except ValueError:
                recomends_dictionary_results['positive_outlook'] = False
        if(is_approved_ceo_element):
            try:
                recomends_dictionary_results['approves_ceo'] = recommends_element.select('i.sqLed')[0].attrs['class'].index('green')>0
            except ValueError:
                recomends_dictionary_results['approves_ceo'] = False

    return recomends_dictionary_results

def extract_rating_info(extracted_review):
    rating_dictionary_results = {}
    rating_category_list = extracted_review.select("div.subRatings span.gdRatings")
    if(len(rating_category_list)>0):
        rating_dictionary_results['ratings_work_life_balance'] = rating_category_list[0]['title']
    if(len(rating_category_list)>1):
        rating_dictionary_results['ratings_culture_values'] = rating_category_list[1]['title']
    if(len(rating_category_list)>2):
        rating_dictionary_results['ratings_career_oportinity'] = rating_category_list[2]['title']
    if(len(rating_category_list)>3):
        rating_dictionary_results['ratings_comp_benefits'] = rating_category_list[3]['title']
    if(len(rating_category_list)>4):
        rating_dictionary_results['ratings_senior_management'] = rating_category_list[4]['title']
    overall_rating_element = extracted_review.select('span.rating span')[0]['title']
    rating_dictionary_results['overall_rating'] = overall_rating_element

    return rating_dictionary_results