import threading 
import subprocess

clusterready = True
index = "cpu"
cluster = "acedi002ks02"
pksapi = "api.pks.dev.aldicn.local"
username = "user1"
password = "user1"

def exec():
   
    print('check the cluster status...')
    c = subprocess.getstatusoutput('pks cluster ' + cluster +' |grep "Last Action State"')
    print(c[1])
    if 'succeeded' in c[1]:
       clusterready = True
    else: 
       clusterready = False 
   
    if clusterready:

       print('get the current autoscalers')
       c = subprocess.getstatusoutput('kubectl get autoscaler -o jsonpath={.items[*].metadata.name}')
       scalernames = c[1].split(" ")
       print(scalernames)
       
       for scalername in scalernames:
          print('get the autoscaler ' + scalername)
          c = subprocess.getstatusoutput('kubectl get autoscaler ' + scalername + ' -o jsonpath={.spec.enabled}')
          print("Enabled? " + c[1])
          if c[1] == "true":
             enabled = True
          else:
             enabled = False
          
          if enabled:

             print('get the autoscaler index')
             c = subprocess.getstatusoutput('kubectl get autoscaler ' + scalername + ' -o jsonpath={.spec.index}')
             print(c[1])
             index = c[1]

             print('get the autoscaler upscale value')
             c = subprocess.getstatusoutput('kubectl get autoscaler ' + scalername + ' -o jsonpath={.spec.upscaleon}')
             print(c[1])
             upscaleon = c[1]

             print('get the autoscaler downscale value')
             c = subprocess.getstatusoutput('kubectl get autoscaler ' + scalername + ' -o jsonpath={.spec.downscaleon}')
             print(c[1])
             downscaleon = c[1]

             print('get the current node data')        
             if index == "cpu":
                c = subprocess.getstatusoutput("kubectl top nodes | awk '//{print $3 }' | sed '1d'")
             else:
                c = subprocess.getstatusoutput("kubectl top nodes | awk '//{print $5 }' | sed '1d'")       

             values = c[1].split("\n")
             sum = 0
             for x in values:
                d = x.replace("%","")
                print("the value of node is: " + d)
                sum = sum + int(d)

             avg = sum/len(values)
             print("The average value of the node is: " + str(avg))
             size = len(values) + 1
 
             if avg > float(upscaleon):
                print('scale out the cluster...')
                c = subprocess.getstatusoutput('pks resize ' + cluster + ' -n ' + str(size) + ' --non-interactive')
                print(c[1])
                break
             if avg < float(downscaleon):
                if len(values)>1:
                   print('scale down the cluster...')
                   size = len(values) - 1
                   c = subprocess.getstatusoutput('pks resize ' + cluster + ' -n ' + str(size) + ' --non-interactive')
                   print(c[1])
                   break

    global timer
    timer = threading.Timer(5, exec)
    timer.start()

print('execute pks login')
c = subprocess.getstatusoutput('pks login -a ' + pksapi + ' -u ' + username + ' -p ' + password + ' -k')
print(c[1])

print('get credentials')
c = subprocess.getstatusoutput('pks get-credentials ' + cluster)
print(c[1])

print('use this context')
c = subprocess.getstatusoutput('kubectl config use-context ' + cluster)
print(c[1])

timer = threading.Timer(1, exec)
timer.start()
