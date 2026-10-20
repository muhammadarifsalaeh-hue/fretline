import { useState } from 'react';
import { cn } from '@/utils/cn';

/** ภาพสำรองเมื่อรูปโหลดไม่ได้ — ดูเป็นดีไซน์ ไม่ใช่รูปแตก */
function GuitarFallback() {
  return (
    <div className="absolute inset-0 grid place-items-center bg-gradient-to-br from-[#262626] to-[#141414]">
      <svg viewBox="0 0 200 200" className="h-1/2 w-1/2 text-gold/40" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
        <g transform="rotate(-40 100 100)">
          <rect x="92" y="4" width="16" height="14" rx="3" />
          <rect x="96" y="18" width="8" height="80" rx="2" />
          <path d="M100 96c-26 0-38 14-34 34-8 4-12 12-10 22 4 20 24 26 44 26s40-6 44-26c2-10-2-18-10-22 4-20-8-34-34-34z" />
          <circle cx="100" cy="134" r="10" />
        </g>
      </svg>
    </div>
  );
}

/**
 * <img> ที่ fade-in เมื่อโหลดเสร็จ และมี fallback เมื่อโหลดไม่ได้
 * ใส่ className ที่ container (เช่น "absolute inset-0") และ imgClassName ที่ตัวรูป
 */
export default function SmartImage({ src, alt = '', className = '', imgClassName = '', priority = false, srcSet, sizes, width, height, fit = 'cover', fallback }) {
  const [status, setStatus] = useState('loading');

  return (
    <div className={cn('overflow-hidden bg-[#1a1a1a]', className)}>
      {status === 'error' || !src ? (
        fallback ?? <GuitarFallback />
      ) : (
        <img
          src={src}
          srcSet={srcSet}
          sizes={sizes}
          alt={alt}
          width={width}
          height={height}
          loading={priority ? 'eager' : 'lazy'}
          fetchpriority={priority ? 'high' : undefined}
          decoding="async"
          onLoad={() => setStatus('loaded')}
          onError={() => setStatus('error')}
          className={cn(
            `h-full w-full ${fit === 'contain' ? 'object-contain' : 'object-cover'} transition-[opacity,transform] duration-700 ease-premium`,
            status === 'loaded' ? 'opacity-100' : 'opacity-0',
            imgClassName,
          )}
        />
      )}
    </div>
  );
}
