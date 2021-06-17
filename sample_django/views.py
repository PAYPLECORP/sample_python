import os

from django.shortcuts import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import requests
import json


# GET /, order.html 렌더링
def order(request):
    user_data = {
        'buyer_no': 2335,
        'buyer_name': '홍길동',
        'buyer_hp': '01012345678',
        'buyer_email': 'test@payple.kr',
        'buy_goods': '휴대폰',
        'buy_total': '1000',
        'order_num': 'test',
        'oid': create_oid()
    }
    return render(request, 'order.html', user_data)


# POST /order_confirm, 결제 확인 렌더링(order_confirm.html)
def order_confirm(request):
    if request.method == 'POST':
        data = {
            'pcd_cpay_ver': request.POST.get('pcd_cpay_ver'),  # 결제창 버전 (Default : 1.0.1)
            'is_direct': request.POST.get('is_direct'),  # 결제창 방식 (DIRECT: Y | POPUP: N)
            'pay_type': request.POST.get('pay_type'),  # 결제수단
            'work_type': request.POST.get('work_type'),  # 결제요청방식
            'card_ver': request.POST.get('card_ver'),  # DEFAULT: 01 (01: 정기결제 플렛폼, 02: 일반결제 플렛폼), 카드결제 시 필수
            'payple_payer_id': request.POST.get('payple_payer_id'),  # 결제자 고유ID (본인인증 된 결제회원 고유 KEY)
            'buyer_no': request.POST.get('buyer_no'),  # 가맹점 회원 고유번호
            'buyer_name': request.POST.get('buyer_name'),  # 결제자 이름
            'buyer_hp': request.POST.get('buyer_hp'),  # 결제자 휴대폰 번호
            'buyer_email': request.POST.get('buyer_email'),  # 결제자 Email
            'buy_goods': request.POST.get('buy_goods'),  # 결제 상품
            'buy_total': request.POST.get('buy_total'),  # 결제 금액
            'buy_istax': request.POST.get('buy_istax'),  # 과세여부 (과세: Y | 비과세(면세): N)
            'buy_taxtotal': request.POST.get('buy_taxtotal'),  # 부가세(복합과세인 경우 필수)
            'order_num': request.POST.get('order_num'),  # 주문번호
            'pay_year': request.POST.get('pay_year'),  # [정기결제] 결제 구분 년도
            'pay_month': request.POST.get('pay_month'),  # [정기결제] 결제 구분 월
            'is_reguler': request.POST.get('is_reguler'),  # 정기결제 여부 (Y | N)
            'is_taxsave': request.POST.get('is_taxsave'),  # 현금영수증 발행여부
            'simple_flag': request.POST.get('simple_flag'),  # 간편결제 여부
            'auth_type': request.POST.get('auth_type'),  # [간편결제/정기결제] 본인인증 방식 (sms : 문자인증 | pwd : 패스워드 인증)
            'hostname': os.environ.get('HOSTNAME')  # 다이렉트 결제창 호출시, 절대경로 세팅을 위한 HOSTNAME 환경변수
        }
        return render(request, 'order_confirm.html', data)
    return redirect('/')


# POST /auth, 가맹점 인증
# 케이스별로 가맹점 인증 요청에 사용하는 요청변수가 다르니, Payple에서 제공하는 가이드를 통해 요청변수를 확인하시길 바랍니다.
# ref: http://docs.payple.kr/card/install/auth
def authenticate(request):
    if request.method == 'POST':
        auth_url = os.environ.get('AUTH_URL')  # 가맹점 인증 URL
        data = {
            'cst_id': os.environ.get('CST_ID'),  # 가맹점 ID (실결제시 .env 파일내 발급받은 운영ID를 작성하시기 바랍니다.)
            'custKey': os.environ.get('CUST_KEY'),  # 가맹점 Key (실결제시 .env 파일내 발급받은 운영Key를 작성하시기 바랍니다.)
        }

        # 가맹점 인증 API를 요청하는 서버와 결제창을 띄우는 서버가 다른 경우 또는 AWS 이용 가맹점인 경우 REFERER 포함
        headers = {'Content-Type': 'application/json;', 'referer': os.environ.get('PCD_HTTP_REFERRER')}
        # 가맹점 인증 URL로 요청변수 및 헤더를 포함하여 POST 요청을 보냄
        response = requests.post(auth_url, data=json.dumps(data), headers=headers).json()

        print('가맹점인증 결과 :', response)
        return HttpResponse(json.dumps(response), content_type="application/json")
    return redirect('/')


# POST /result, 결제창으로 받은 리턴받은 결과 값 렌더링(order_result.html)
@csrf_exempt
def order_result(request):
    if request.method == 'POST':
        # 공통 수신 데이터
        data = {
            'PCD_PAY_RST': request.POST.get('PCD_PAY_RST', ''),  # 결제요청 결과(success|error)
            'PCD_PAY_MSG': request.POST.get('PCD_PAY_MSG', ''),  # 결제요청 결과 메시지
            'PCD_PAY_WORK': request.POST.get('PCD_PAY_WORK', ''),
            # 결제요청 업무구분 (AUTH : 본인인증+계좌등록, CERT: 본인인증+계좌등록+결제요청등록(최종 결제승인요청 필요), PAY: 본인인증+계좌등록+결제완료)
            'PCD_AUTH_KEY': request.POST.get('PCD_AUTH_KEY', ''),  # 결제용 인증키
            'PCD_PAY_REQKEY': request.POST.get('PCD_PAY_REQKEY', ''),  # 결제요청 고유 KEY
            'PCD_PAY_COFURL': request.POST.get('PCD_PAY_COFURL', ''),  # 결제승인요청 URL
            'PCD_PAY_OID': request.POST.get('PCD_PAY_OID', ''),  # 주문번호
            'PCD_PAY_TYPE': request.POST.get('PCD_PAY_TYPE', ''),  # 결제 방법 (transfer | card)
            'PCD_PAYER_ID': request.POST.get('PCD_PAYER_ID', ''),  # 카드등록 후 리턴받은 빌링키
            'PCD_PAYER_NO': request.POST.get('PCD_PAYER_NO', ''),  # 가맹점 회원 고유번호
            'PCD_PAY_GOODS': request.POST.get('PCD_PAY_GOODS', ''),  # 결제 상품
            'PCD_PAY_TOTAL': request.POST.get('PCD_PAY_TOTAL', ''),  # 결제 금액
            'PCD_PAY_TAXTOTAL': request.POST.get('PCD_PAY_TAXTOTAL', ''),
            # 복합과세(과세+면세) 주문건에 필요한 금액이며 가맹점에서 전송한 값을 부가세로 설정합니다. 과세 또는 비과세의 경우 사용하지 않습니다.
            'PCD_PAY_ISTAX': request.POST.get('PCD_PAY_ISTAX', ''),  # 과세설정 (Default: Y, 과세:Y, 복합과세:Y, 비과세: N)
            'PCD_PAYER_EMAIL': request.POST.get('PCD_PAYER_EMAIL', ''),  # 결제자 Email
            'PCD_PAY_YEAR': request.POST.get('PCD_PAY_YEAR', ''),  # 결제 구분 년도 (PCD_REGULER_FLAG 사용시 응답)
            'PCD_PAY_MONTH': request.POST.get('PCD_PAY_MONTH', ''),  # 결제 구분 월 (PCD_REGULER_FLAG 사용시 응답)
            'PCD_PAY_TIME': request.POST.get('PCD_PAY_TIME', ''),  # 결제 시간 (format: yyyyMMddHHmmss, ex: 20210610142219)
            'PCD_REGULER_FLAG': request.POST.get('PCD_REGULER_FLAG', ''),  # 정기결제 여부 (Y | N)
            'PCD_TAXSAVE_RST': request.POST.get('PCD_TAXSAVE_RST', ''),  # 현금영수증 발행결과 (Y | N)
            'PCD_PAYER_NAME': request.POST.get('PCD_PAYER_NAME', ''),  # 결제자 이름
        }

        # 계좌결제시 수신 데이터
        if data.get('PCD_PAY_TYPE') == 'transfer':
            data_by_type = {
                'PCD_PAY_BANK': request.POST.get('PCD_PAY_BANK', ''),  # [계좌결제] 은행코드
                'PCD_PAY_BANKNAME': request.POST.get('PCD_PAY_BANKNAME', ''),  # [계좌결제]은행명
                'PCD_PAY_BANKNUM': request.POST.get('PCD_PAY_BANKNUM', ''),  # [계좌결제] 계좌번호(중간 6자리 * 처리)
            }
        # 카드결제시 수신 데이터
        elif data.get('PCD_PAY_TYPE') == 'card':
            data_by_type = {
                'PCD_PAY_CARDNAME': request.POST.get('PCD_PAY_CARDNAME', ''),  # [카드결제] 카드사명
                'PCD_PAY_CARDNUM': request.POST.get('PCD_PAY_CARDNUM', ''),  # [카드결제] 카드번호 (ex: 1234-****-****-5678)
                'PCD_PAY_CARDTRADENUM': request.POST.get('PCD_PAY_CARDTRADENUM', ''),  # [카드결제] 카드결제 거래번호
                'PCD_PAY_CARDAUTHNO': request.POST.get('PCD_PAY_CARDAUTHNO', ''),  # [카드결제] 카드결제 승인번호
                'PCD_PAY_CARDRECEIPT': request.POST.get('PCD_PAY_CARDRECEIPT', ''),  # [카드결제] 카드전표 URL
            }
        data.update(data_by_type)

        print('order_result Value :', data)
        return render(request, 'order_result.html', data)
    return redirect('/')


# POST /payconfirm, 결제요청 재컨펌 (PCD_PAY_WORK : CERT)
# ref (bank): http://docs.payple.kr/bank/pay/regular
# ref (card): http://docs.payple.kr/card/pay/regular
def pay_confirm(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        pay_confirm_url = body.get('PCD_PAY_COFURL')  # (필수) 결제승인요청 URL
        data = {
            'PCD_CST_ID': os.environ.get('CST_ID'),  # (필수) 가맹점 ID (실결제시 .env 파일내 발급받은 운영ID를 작성하시기 바랍니다.)
            'PCD_CUST_KEY': os.environ.get('CUST_KEY'),  # (필수) 가맹점 Key (실결제시 .env 파일내 발급받은 운영Key를 작성하시기 바랍니다.)
            'PCD_AUTH_KEY': body.get('PCD_AUTH_KEY', ''),  # (필수) 결제용 인증키
            'PCD_PAYER_ID': body.get('PCD_PAYER_ID', ''),  # (필수) 결제자 고유ID
            'PCD_PAY_REQKEY': body.get('PCD_PAY_REQKEY', ''),  # (필수) 결제요청 고유KEY
        }

        # 요청하는 서버와 결제창을 띄우는 서버가 다른 경우 또는 AWS 이용 가맹점인 경우 REFERER 포함
        headers = {'Content-Type': 'application/json;', 'referer': os.environ.get('PCD_HTTP_REFERRER')}
        # 결제승인요청 URL로 요청변수 및 헤더를 포함하여 POST 요청을 보냄
        response = requests.post(pay_confirm_url, data=json.dumps(data), headers=headers).json()

        print('결제승인요청 결과 :', response)
        return HttpResponse(json.dumps(response), content_type="application/json")
    return redirect('/')


# POST /refund, 환불(승인취소)
# ref (bank): http://docs.payple.kr/bank/pay/cancel
# ref (card): http://docs.payple.kr/card/pay/cancel
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

        body = json.loads(request.body)
        refund_url = auth_data.get('return_url')  # (필수) 리턴 받은 환불(승인취소) URL
        refund_data = {
            'PCD_CST_ID': auth_data.get('cst_id'),  # (필수) 리턴 받은 cst_id Token
            'PCD_CUST_KEY': auth_data.get('custKey'),  # (필수) 리턴 받은 custKey Token
            'PCD_AUTH_KEY': auth_data.get('AuthKey'),  # (필수) 리턴 받은 AuthKey Token
            'PCD_REFUND_KEY': os.environ.get('PCD_REFUND_KEY'),  # (필수) 환불서비스 Key (관리자페이지 상점정보 > 기본정보에서 확인하실 수 있습니다.)
            'PCD_PAYCANCEL_FLAG': "Y",  # (필수) 'Y' – 고정 값
            'PCD_PAY_OID': body.get('PCD_PAY_OID', ''),  # (필수) 주문번호
            'PCD_PAY_DATE': body.get('PCD_PAY_DATE', ''),  # (필수) 취소할 원거래일자
            'PCD_REFUND_TOTAL': body.get('PCD_REFUND_TOTAL', ''),  # (필수) 환불 요청금액 (기존 결제금액보다 적은 금액 입력 시 부분취소로 진행)
            'PCD_REGULER_FLAG': body.get('PCD_REGULER_FLAG', 'N'),  # (선택) 월 중복결제 방지 Y(사용) | N(그 외)
            'PCD_PAY_YEAR': body.get('PCD_PAY_YEAR', ''),  # (선택) 결제 구분 년도
            'PCD_PAY_MONTH': body.get('PCD_PAY_MONTH', '')  # (선택) 결제 구분 월
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
