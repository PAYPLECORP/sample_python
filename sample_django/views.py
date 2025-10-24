import os

from django.shortcuts import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import requests
import json


# GET /, order.html 렌더링
def order(request):
    user_data = {
        'payer_no': 2335,
        'payer_name': '홍길동',
        'payer_hp': '01012345678',
        'payer_email': 'test@payple.kr',
        'pay_goods': '휴대폰',
        'pay_total': '1000',
        'pay_oid': create_oid()
    }
    return render(request, 'order.html', user_data)


# POST /order_confirm, 결제 확인 렌더링(order_confirm.html)
def order_confirm(request):
    if request.method == 'POST':
        data = {
            'client_key': os.environ.get('CLIENT_KEY'),  # 파트너 인증 - 클라이언트 키(clientKey)
            'is_direct': request.POST.get('is_direct'),  # 결제창 방식 (DIRECT: Y | POPUP: N)
            'pay_type': request.POST.get('pay_type'),  # 결제수단
            'pay_work': request.POST.get('pay_work'),  # 결제요청방식
            'card_ver': request.POST.get('card_ver'),  # DEFAULT: 01 (01: 정기결제 플렛폼, 02: 일반결제 플렛폼), 카드결제 시 필수
            'payer_id': request.POST.get('payer_id'),  # 결제자 고유ID (본인인증 된 결제회원 고유 KEY)
            'payer_no': request.POST.get('payer_no'),  # 가맹점 회원 고유번호
            'payer_name': request.POST.get('payer_name'),  # 결제자 이름
            'payer_hp': request.POST.get('payer_hp'),  # 결제자 휴대폰 번호
            'payer_email': request.POST.get('payer_email'),  # 결제자 Email
            'pay_goods': request.POST.get('pay_goods'),  # 결제 상품
            'pay_total': request.POST.get('pay_total'),  # 결제 금액
            'pay_istax': request.POST.get('pay_istax'),  # 과세여부 (과세: Y | 비과세(면세): N)
            'pay_taxtotal': request.POST.get('pay_taxtotal'),  # 부가세(복합과세인 경우 필수)
            'pay_oid': request.POST.get('pay_oid'),  # 주문번호
            'taxsave_flag': request.POST.get('taxsave_flag'),  # 현금영수증 발행여부
            'simple_flag': request.POST.get('simple_flag'),  # 간편결제 여부
            'payer_authtype': request.POST.get('payer_authtype'),  # [간편결제/정기결제] 본인인증 방식 (sms : 문자인증 | pwd : 패스워드 인증)
            'pay_method_flag': request.POST.get('pay_method_flag'),  # 결제 수단
            'hostname': os.environ.get('HOSTNAME') # 다이렉트 결제창 호출시, 절대경로 세팅을 위한 HOSTNAME 환경변수
        }
        return render(request, 'order_confirm.html', data)
    return redirect('/')


# POST /auth, 가맹점 인증
# 케이스별로 가맹점 인증 요청에 사용하는 요청변수가 다르니, Payple에서 제공하는 가이드를 통해 요청변수를 확인하시길 바랍니다.
def authenticate(request):
    if request.method == 'POST':
        auth_url = os.environ.get('AUTH_URL')  # 가맹점 인증 URL
        data = {
            'cst_id': os.environ.get('CST_ID'),  # 가맹점 ID (실결제시 .env 파일내 발급받은 운영ID를 작성하시기 바랍니다.)
            'custKey': os.environ.get('CUST_KEY'),  # 가맹점 Key (실결제시 .env 파일내 발급받은 운영Key를 작성하시기 바랍니다.)
        }

        # 가맹점 인증 API를 요청하는 서버와 결제창을 띄우는 서버가 다른 경우 또는 AWS 이용 가맹점인 경우 REFERER 포함
        headers = {'Content-Type': 'application/json;', 'referer': os.environ.get('PCD_HTTP_REFERRER')}

        # 요청 정보 로그 출력
        print('========== /auth 요청 정보 ==========')
        print('요청 URL:', auth_url)
        print('요청 Headers:', headers)
        print('요청 Body:', json.dumps(data, ensure_ascii=False, indent=2))
        print('====================================')

        # 가맹점 인증 URL로 요청변수 및 헤더를 포함하여 POST 요청을 보냄
        response = requests.post(auth_url, data=json.dumps(data), headers=headers).json()

        print('가맹점인증 결과 :', response)
        return HttpResponse(json.dumps(response), content_type="application/json")
    return redirect('/')


# POST /result, 결제창으로 받은 리턴받은 결과 값 렌더링(order_result.html)
@csrf_exempt
def order_result(request):
    if request.method == 'POST':
        # 결제 결과를 HTML 테이블 형식으로 생성
        result_html = ""
        for key, value in request.POST.items():
            result_html += f"{key} => {value}<br>"

        # 공통 수신 데이터
        data = {
            'result': result_html,  # 전체 결과를 HTML 테이블로
            'pay_rst': request.POST.get('PCD_PAY_RST', ''),  # 결제요청 결과(success|error)
            'pay_msg': request.POST.get('PCD_PAY_MSG', ''),  # 결제요청 결과 메시지
            'pay_work': request.POST.get('PCD_PAY_WORK', ''),  # 결제요청 업무구분
            'auth_key': request.POST.get('PCD_AUTH_KEY', ''),  # 결제용 인증키
            'pay_reqkey': request.POST.get('PCD_PAY_REQKEY', ''),  # 결제요청 고유 KEY
            'pay_cofurl': request.POST.get('PCD_PAY_COFURL', ''),  # 결제승인요청 URL
            'pay_oid': request.POST.get('PCD_PAY_OID', ''),  # 주문번호
            'pay_type': request.POST.get('PCD_PAY_TYPE', ''),  # 결제 방법 (transfer | card)
            'payer_id': request.POST.get('PCD_PAYER_ID', ''),  # 카드등록 후 리턴받은 빌링키
            'payer_no': request.POST.get('PCD_PAYER_NO', ''),  # 가맹점 회원 고유번호
            'pay_goods': request.POST.get('PCD_PAY_GOODS', ''),  # 결제 상품
            'pay_total': request.POST.get('PCD_PAY_TOTAL', ''),  # 결제 금액
            'pay_taxtotal': request.POST.get('PCD_PAY_TAXTOTAL', ''),  # 부가세
            'pay_istax': request.POST.get('PCD_PAY_ISTAX', ''),  # 과세설정
            'payer_email': request.POST.get('PCD_PAYER_EMAIL', ''),  # 결제자 Email
            'pay_time': request.POST.get('PCD_PAY_TIME', ''),  # 결제 시간
            'taxsave_rst': request.POST.get('PCD_TAXSAVE_RST', ''),  # 현금영수증 발행결과
            'payer_name': request.POST.get('PCD_PAYER_NAME', ''),  # 결제자 이름
            'pay_method': request.POST.get('PCD_PAY_METHOD', ''),  # 결제 수단
            'easy_pay_method': request.POST.get('PCD_EASY_PAY_METHOD', ''),  # 간편결제 수단
            'pay_bankacctype': request.POST.get('PCD_PAY_BANKACCTYPE', ''),  # 계좌유형
            'tx_key': request.POST.get('PCD_TX_KEY', ''),  # 거래 고유키
            'pay_date': request.POST.get('PCD_PAY_TIME', '')[:8] if request.POST.get('PCD_PAY_TIME') else '',  # 결제일자 (YYYYMMDD)
        }

        # 계좌결제시 수신 데이터
        if request.POST.get('PCD_PAY_TYPE') == 'transfer':
            data.update({
                'pay_bank': request.POST.get('PCD_PAY_BANK', ''),  # [계좌결제] 은행코드
                'pay_bankname': request.POST.get('PCD_PAY_BANKNAME', ''),  # [계좌결제]은행명
                'pay_banknum': request.POST.get('PCD_PAY_BANKNUM', ''),  # [계좌결제] 계좌번호(중간 6자리 * 처리)
            })
        # 카드결제시 수신 데이터
        elif request.POST.get('PCD_PAY_TYPE') == 'card':
            data.update({
                'pay_cardname': request.POST.get('PCD_PAY_CARDNAME', ''),  # [카드결제] 카드사명
                'pay_cardnum': request.POST.get('PCD_PAY_CARDNUM', ''),  # [카드결제] 카드번호
                'pay_cardtradenum': request.POST.get('PCD_PAY_CARDTRADENUM', ''),  # [카드결제] 카드결제 거래번호
                'pay_cardauthno': request.POST.get('PCD_PAY_CARDAUTHNO', ''),  # [카드결제] 카드결제 승인번호
                'pay_cardreceipt': request.POST.get('PCD_PAY_CARDRECEIPT', ''),  # [카드결제] 카드전표 URL
            })

        print('order_result Value :', data)
        return render(request, 'order_result.html', data)
    return redirect('/')


# POST /payconfirm, 결제요청 재컨펌 (PCD_PAY_WORK : CERT)
@csrf_exempt
def pay_confirm(request):
    if request.method == 'POST':
        # FormData로 전송된 데이터를 받음
        pay_confirm_url = request.POST.get('PCD_PAY_COFURL')  # (필수) 결제승인요청 URL
        data = {
            'PCD_CST_ID': os.environ.get('CST_ID'),  # (필수) 가맹점 ID (실결제시 .env 파일내 발급받은 운영ID를 작성하시기 바랍니다.)
            'PCD_CUST_KEY': os.environ.get('CUST_KEY'),  # (필수) 가맹점 Key (실결제시 .env 파일내 발급받은 운영Key를 작성하시기 바랍니다.)
            'PCD_AUTH_KEY': request.POST.get('PCD_AUTH_KEY', ''),  # (필수) 결제용 인증키
            'PCD_PAYER_ID': request.POST.get('PCD_PAYER_ID', ''),  # (필수) 결제자 고유ID
            'PCD_PAY_REQKEY': request.POST.get('PCD_PAY_REQKEY', ''),  # (필수) 결제요청 고유KEY
        }

        # 요청하는 서버와 결제창을 띄우는 서버가 다른 경우 또는 AWS 이용 가맹점인 경우 REFERER 포함
        headers = {'Content-Type': 'application/json;', 'referer': os.environ.get('PCD_HTTP_REFERRER')}
        # 결제승인요청 URL로 요청변수 및 헤더를 포함하여 POST 요청을 보냄
        response = requests.post(pay_confirm_url, data=json.dumps(data), headers=headers).json()

        print('결제승인요청 결과 :', response)
        return HttpResponse(json.dumps(response), content_type="application/json")
    return redirect('/')


# POST /refund, 환불(승인취소)
@csrf_exempt
def pay_refund(request):
    if request.method == 'POST':
        auth_url = os.environ.get('AUTH_URL')  # 가맹점 인증 URL
        data = {
            'cst_id': os.environ.get('CST_ID'),  # 가맹점 ID (실결제시 .env 파일내 발급받은 운영ID를 작성하시기 바랍니다.)
            'custKey': os.environ.get('CUST_KEY'),  # 가맹점 Key (실결제시 .env 파일내 발급받은 운영Key를 작성하시기 바랍니다.)
            'PCD_PAYCANCEL_FLAG': 'Y',  # 승인취소(환불) 추가요청변수
        }

        headers = {'Content-Type': 'application/json;', 'referer': os.environ.get('PCD_HTTP_REFERRER')}
        auth_data = requests.post(auth_url, data=json.dumps(data), headers=headers).json()

        # FormData로 전송된 데이터를 받음
        refund_url = auth_data.get('return_url')  # (필수) 리턴 받은 환불(승인취소) URL
        refund_data = {
            'PCD_CST_ID': auth_data.get('cst_id'),  # (필수) 리턴 받은 cst_id Token
            'PCD_CUST_KEY': auth_data.get('custKey'),  # (필수) 리턴 받은 custKey Token
            'PCD_AUTH_KEY': auth_data.get('AuthKey'),  # (필수) 리턴 받은 AuthKey Token
            'PCD_REFUND_KEY': os.environ.get('PCD_REFUND_KEY'),  # (필수) 환불서비스 Key (관리자페이지 상점정보 > 기본정보에서 확인하실 수 있습니다.)
            'PCD_PAYCANCEL_FLAG': "Y",  # (필수) 'Y' – 고정 값
            'PCD_PAY_OID': request.POST.get('PCD_PAY_OID', ''),  # (필수) 주문번호
            'PCD_PAY_DATE': request.POST.get('PCD_PAY_DATE', ''),  # (필수) 취소할 원거래일자
            'PCD_REFUND_TOTAL': request.POST.get('PCD_REFUND_TOTAL', ''),  # (필수) 환불 요청금액 (기존 결제금액보다 적은 금액 입력 시 부분취소로 진행)
            'PCD_REGULER_FLAG': request.POST.get('PCD_REGULER_FLAG', 'N'),  # (선택) 월 중복결제 방지 Y(사용) | N(그 외)
            'PCD_PAY_YEAR': request.POST.get('PCD_PAY_YEAR', ''),  # (선택) 결제 구분 년도
            'PCD_PAY_MONTH': request.POST.get('PCD_PAY_MONTH', '')  # (선택) 결제 구분 월
        }

        # 요청하는 서버와 결제창을 띄우는 서버가 다른 경우 또는 AWS 이용 가맹점인 경우 REFERER 포함
        headers = {'Content-Type': 'application/json;', 'referer': os.environ.get('PCD_HTTP_REFERRER')}
        # 결제승인요청 URL로 요청변수 및 헤더를 포함하여 POST 요청을 보냄
        response = requests.post(refund_url, data=json.dumps(refund_data), headers=headers).json()

        print('승인취소(환불) 결과 :', response)
        return HttpResponse(json.dumps(response), content_type="application/json")
    return redirect('/')


# Oid 생성 함수
# 리턴 예시: test202105281622170718461
def create_oid():
    return 'test' + datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
