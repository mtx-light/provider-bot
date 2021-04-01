with open('../domains/internet/balance_and_home_service/train.txt', 'w') as result_file:
    with open('../domains/internet/home_service/train.txt') as src1:
            for l1 in src1.readlines():
                with open('/home/max/bots/provider-bot/provider_bot/domains/internet/check_balance/train.txt') as src2:
                    for l2 in src2.readlines():
                        result_file.write(l1.strip() + " і " + l2)
                        result_file.write(l1.strip() + " а також " + l2)