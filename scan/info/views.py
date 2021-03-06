from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, Http404
from django.core.files.uploadedfile import InMemoryUploadedFile
from asset.models import DomainList
import whois
import nmap
from urllib import request as r
import os
import subprocess

headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3'
}


def who_is(request, action=None):
    if request.method == 'POST':

        target = request.POST.get('arg')
        res = whois.whois(target)
        result = request.GET.get('result')
        result = res
        return render(request, 'info/who_is.html', {'result': result})

    else:
        return render(request, 'info/who_is.html')


def subdomain_scan(request):
    if request.method == 'POST':
        domain_list = DomainList.objects.all()
        data = {
            'domain_list': domain_list,
        }
        target = request.POST.get('id_tgt_select[]')

        return render(request, 'info/subdomain_scan.html', data)

    else:
        domain_list = DomainList.objects.all()
        data = {
            'domain_list': domain_list,
        }
        return render(request, 'info/subdomain_scan.html', data)


def port_scan(request):
    if request.method == 'POST':

        techniques_list = ['-sS', '-sT', '-sA', '-sU']
        speed_list = ['-T0', '-T1','-T2','-T3','-T5']
        service_list = ['-sV', '--version-intensity', '--version-light', '--version-all']
        result = request.GET.get('result')
        target = request.POST.get('ip')
        techniques = request.POST.get('techniques_tgt_select[]')
        service = request.POST.get('service_tgt_select[]')
        port = request.POST.get('arg', None)
        speed = request.POST.get('speed_tgt_select[]')
        
        defaultcmd = 'Pn'
        target_list = []
        # 判断是否批量扫描
        if bool(target) is True:
            target = request.POST.get('ip')
            target_list.append(target)

        elif bool(target) is False:

            file_obj = request.FILES.get('file_path')
            with open('customers.txt', mode='wb') as f:

                for chunk in file_obj:
                    ip = chunk.decode().strip('\n')
                    target_list.append(ip)

        # 判断端口，定义arguments
        if port == 'None':
            cmd = service + ' ' + defaultcmd + ' ' + speed
        else:
            portcmd = '-p' + port
            cmd = service + ' ' + defaultcmd + ' ' + portcmd+ ' ' + speed

        # 开始扫描，写入xml文件
        nm = nmap.PortScanner()
        targethost = ' '.join(target_list)
        nm.scan(hosts=targethost, arguments=cmd)
        commandline = nm.command_line()
        with open('templates/nmap/info.xml', 'w') as f:
            f.write(nm.get_nmap_last_output())
            f.close()
        info = '完成' + targethost + '的扫描!'
        # 转换xml到html
        os_cmd = 'xsltproc templates/nmap/info.xml info/nmap-xsl/http-services.xsl -o templates/nmap/info.html'
        xsltproc_cmd = subprocess.Popen(str(os_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        data = {
            'ip': target,
            'techniques_list': techniques_list,
            'service_list': service_list,
            'speed_list': speed_list,
            'arg': port,
            'cmd': commandline,
            'result': info
        }

        return render(request, 'info/port_scan.html', data)

    elif request.method == 'GET':

        target = request.POST.get('ip', None)
        techniques_list = ['-sS | TCP SYN Scan', '-sT | Connect Scan', '-sA | ACK Scan', '-sU | UDP Scan']
        speed_list = ['-T0', '-T1', '-T2', '-T3', '-T5']
        service_list = ['-sV', '--version-intensity', '--version-light', '--version-all']
        data = {
            'speed_list': speed_list,
            'techniques_list': techniques_list,
            'service_list': service_list,
        }

        return render(request, 'info/port_scan.html', data)


def namp_result(request):
    return render(request, 'nmap/info.html')


def identify_web(request):
    return HttpResponse('identify web')


def ip_blacklist(request):
    feed_list = ['Cisco Talos', 'Abuse.ch勒索软件']
    if request.method == 'POST':

        target = request.POST.get('feed_tgt_select[]')

        if target == 'Cisco Talos':

            target_ulr = 'https://talosintelligence.com/documents/ip-blacklist'
            html = r.Request(target_ulr, headers=headers)
            res = r.urlopen(html).read()
            res = res.decode('utf-8')

            data = {
                'feed_list': feed_list,
                'result': res
            }

            return render(request, 'info/ip_blacklist.html', data)

        elif target == 'Abuse.ch勒索软件':

            target_ulr = 'https://ransomwaretracker.abuse.ch/downloads/RW_IPBL.txt'
            html = r.Request(target_ulr, headers=headers)
            res = r.urlopen(html).read()
            res = res.decode('utf-8')
            data = {
                'feed_list': feed_list,
                'result': res
            }

            return render(request, 'info/ip_blacklist.html', data)
    else:

        data = {
            'feed_list': feed_list,
        }

        return render(request, 'info/ip_blacklist.html', data)
