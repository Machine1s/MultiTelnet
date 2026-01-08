FROM alpine:latest

# 安装 SSH 和 Telnet 相关包
RUN apk add --no-cache openssh-server busybox-extras bash

# 配置 SSH
RUN ssh-keygen -A && \
    echo 'root:admin123' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# 创建启动脚本：同时启动 sshd 和 telnetd
# 增加修改主机名的逻辑，模拟现场的复杂提示符提示
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'if [ -n "$HOSTNAME_CUSTOM" ]; then hostname "$HOSTNAME_CUSTOM"; fi' >> /start.sh && \
    echo '/usr/sbin/sshd' >> /start.sh && \
    echo 'exec /usr/sbin/telnetd -F -p 23 -l /bin/sh' >> /start.sh && \
    chmod +x /start.sh

EXPOSE 22 23

CMD ["/start.sh"]
