#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patient Agent API 服务器启动脚本
支持多种部署模式
"""

import os
import sys
import argparse
from app import app

def main():
    parser = argparse.ArgumentParser(description='Patient Agent API 服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--workers', type=int, default=1, help='工作进程数 (生产环境)')
    parser.add_argument('--mode', choices=['dev', 'prod'], default='dev', help='运行模式')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Patient Agent API 服务器")
    print("=" * 60)
    print(f"模式: {args.mode}")
    print(f"地址: http://{args.host}:{args.port}")
    print(f"调试: {'开启' if args.debug else '关闭'}")
    print("=" * 60)
    
    if args.mode == 'dev':
        # 开发模式
        print("启动开发服务器...")
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    else:
        # 生产模式
        try:
            import gunicorn.app.wsgiapp as wsgi
            print("启动生产服务器 (Gunicorn)...")
            
            # 构建Gunicorn参数
            sys.argv = [
                'gunicorn',
                '--bind', f'{args.host}:{args.port}',
                '--workers', str(args.workers),
                '--worker-class', 'sync',
                '--timeout', '120',
                '--keep-alive', '2',
                '--max-requests', '1000',
                '--max-requests-jitter', '100',
                '--preload',
                'app:app'
            ]
            
            wsgi.run()
            
        except ImportError:
            print("警告: 未安装Gunicorn，使用Flask开发服务器")
            print("生产环境建议安装: pip install gunicorn")
            app.run(
                host=args.host,
                port=args.port,
                debug=False
            )

if __name__ == '__main__':
    main()









