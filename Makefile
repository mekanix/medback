.include <name.py>

SERVICE != echo ${app_name}
REGGAE_PATH := /usr/local/share/reggae
USE_FREENIT = YES

.include <${REGGAE_PATH}/mk/service.mk>
