#!/usr/bin/env bash
echo '{"channel":"#test", "message":"startup", "action": "message"}'
echo '{"action":"plugin", "method":"load", "name":"bar", "code": "#!/usr/bin/env python\nimport python"}'
sleep 1
exit 1
#echo '{"action":"plugin", "method": "load", "name":
