SSHSOCKET=~/.ssh/ubuntu@13.58.110.76
ssh -i ~/Documents/GitHub/ActivityBot/credentials/ricardoserver.pem -M -f -N -o ControlPath=$SSHSOCKET ubuntu@13.58.110.76
scp -o ControlPath=$SSHSOCKET *.py ubuntu@13.58.110.76:~/ActivityBot
scp -o ControlPath=$SSHSOCKET credentials/* ubuntu@13.58.110.76:~/ActivityBot/credentials
ssh -S $SSHSOCKET -O exit ubuntu@13.58.110.76
