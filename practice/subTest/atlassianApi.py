from atlassian import Confluence

my_access_token = "NTQ3MjAzMjgwMTE3OmQmIKJAUmvyCLJ9gTbajyVyBsqV"

page_no = 3744176 
confluence = Confluence(
 url='https://share.nice.co.kr',
 token=my_access_token
)

print(confluence.get_page_space(page_no))

space='intern'
title='create_page 테스트'
parent_id=149759446
 
status = confluence.create_page(space=space, parent_id=parent_id, title=title, body="페이지 생성 테스트 입니다.")
 
print(status)