import json
import re
import random

def extract_active_chemical(item):
    short_content = item.get('short_content', '')
    match = re.search(r'\nThành phần,([^\n]+)', short_content)
    return match.group(1) if match else None

def main():
    input_file = 'Longchau/shop.json'
    output_file = 'add_filterd.json' #'drug_filtered.json'
    
    # Load the JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Filter the data to get only "breadcrumb": "Thuốc" samples
    filtered_data = [item for item in data if "Thuốc" in item.get("breadcrumb", [])] #"Thuốc"
    
    # Keep only the specified keys in each JSON object
    keys_to_keep = ['url', 'breadcrumb', 'title', 'short_content']
    final_data = [{key: item.get(key, None) for key in keys_to_keep} for item in filtered_data]
    
    # Further filter the data based on specified unique breadcrumb values
    # Uncomment this for drug
    specified_unique_breadcrumbs = [
    "Kháng sinh Aminoglycoside",
    "Kháng sinh nhóm Penicillin",
    "Các loại kháng sinh khác",
    "Thuốc kháng sinh (đường toàn thân)",
    "Cephalosporin",
    "Macrolid",
    "Quinolon",
    "Thuốc kháng viêm không steroid",
    "Kháng viêm dạng men",
    "Vitamin C",
    "Vitamin & khoáng chất",
    "Vitamin & khoáng chất (trước & sau sinh)/ Thuốc trị thiếu máu",
    "Vitamin Nhóm B/ Vitamin nhóm B, C kết hợp",
    "Vitamin A, D & E",
    "Thuốc chống sung huyết mũi & các chế phẩm khác dùng cho mũi",
    "Thuốc giảm đau (opioid)",
    "Thuốc giảm đau (không opioid) & hạ sốt",
    "Dị ứng & hệ miễn dịch",
    "Hệ hô hấp",
    "Thuốc trị hen & bệnh phổi tắc nghẽn mạn tính",
    "Các thuốc khác có tác dụng trên hệ hô hấp",
    "Thuốc ho & cảm"
    ]
    
    # # Further filter the data based on specified unique breadcrumb values
    # specified_unique_breadcrumbs = [
    #     "Hô hấp, ho, xoang",
    #     "Tăng sức đề kháng, miễn dịch",
    #     "Dạ dày, tá tràng",
    #     "Dinh dưỡng trẻ em",
    #     "Bổ sung Kẽm & Magie",
    #     "Bổ sung Sắt & Axit Folic",
    #     "Dầu cá, Omega 3, DHA",
    #     "Vitamin C các loại",
    #     "Vitamin E các loại",
    #     "Thực phẩm chức năng"
    # ]
    
    further_filtered_data = [
        {**item, 'breadcrumb': [breadcrumb for breadcrumb in item.get('breadcrumb', []) 
                                if breadcrumb in specified_unique_breadcrumbs]}
        for item in final_data
        if any(breadcrumb in specified_unique_breadcrumbs for breadcrumb in item.get('breadcrumb', []))
    ]
    
    # Update each dictionary with new keys: Hoạt chất and Số lượng
    for item in further_filtered_data:
        item['Hoạt chất'] = extract_active_chemical(item)
        item['Số lượng'] = random.randint(10, 100) * 100
    
    # Change the key names in each dictionary
    key_name_mapping = {
        'breadcrumb': 'Phân loại',
        'title': 'Biệt dược',
        'short_content': 'Mô tả ngắn'
    }
    updated_further_filtered_data = [
        {key_name_mapping.get(key, key): value for key, value in item.items()} 
        for item in further_filtered_data
    ]
    
    # Write the updated data to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(updated_further_filtered_data, file)
    
    print(len(data))
    print(len(updated_further_filtered_data))

if __name__ == "__main__":
    main()
