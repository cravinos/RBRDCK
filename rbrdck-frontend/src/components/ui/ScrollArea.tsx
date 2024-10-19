import React, { useRef, useEffect, useState } from 'react'

interface ScrollAreaProps {
  className?: string
  children: React.ReactNode
}

export const ScrollArea: React.FC<ScrollAreaProps> = ({ className, children }) => {
  const contentRef = useRef<HTMLDivElement>(null)
  const scrollTrackRef = useRef<HTMLDivElement>(null)
  const scrollThumbRef = useRef<HTMLDivElement>(null)
  const observer = useRef<ResizeObserver | null>(null)
  const [thumbHeight, setThumbHeight] = useState(20)
  const [scrollStartPosition, setScrollStartPosition] = useState<number | null>(null)
  const [initialScrollTop, setInitialScrollTop] = useState<number>(0)
  const [isDragging, setIsDragging] = useState(false)

  function handleResize(ref: HTMLDivElement, trackSize: number) {
    const { clientHeight, scrollHeight } = ref
    setThumbHeight(Math.max((clientHeight / scrollHeight) * trackSize, 20))
  }

  function handleScrollButton(direction: 'up' | 'down') {
    const { current } = contentRef
    if (current) {
      const scrollAmount = direction === 'down' ? 200 : -200
      current.scrollBy({ top: scrollAmount, behavior: 'smooth' })
    }
  }

  function handleTrackClick(e: React.MouseEvent<HTMLDivElement>) {
    const { current: trackCurrent } = scrollTrackRef
    const { current: contentCurrent } = contentRef
    if (trackCurrent && contentCurrent) {
      const { clientY } = e
      const target = e.target as HTMLDivElement
      const rect = target.getBoundingClientRect()
      const trackTop = rect.top
      const thumbOffset = -(thumbHeight / 2)
      const clickRatio = (clientY - trackTop + thumbOffset) / trackCurrent.clientHeight
      const scrollAmount = Math.floor(clickRatio * contentCurrent.scrollHeight)
      contentCurrent.scrollTo({
        top: scrollAmount,
        behavior: 'smooth'
      })
    }
  }

  const handleThumbPosition = () => {
    if (
      !contentRef.current ||
      !scrollTrackRef.current ||
      !scrollThumbRef.current
    ) {
      return
    }
    const { scrollTop: contentTop, scrollHeight: contentHeight } =
      contentRef.current
    const { clientHeight: trackHeight } = scrollTrackRef.current
    let newTop = (+contentTop / +contentHeight) * trackHeight
    newTop = Math.min(newTop, trackHeight - thumbHeight)
    const thumb = scrollThumbRef.current
    thumb.style.top = `${newTop}px`
  }

  const handleThumbMousedown = (e: React.MouseEvent) => {
    setScrollStartPosition(e.clientY)
    if (contentRef.current) setInitialScrollTop(contentRef.current.scrollTop)
    setIsDragging(true)
  }

  const handleThumbMouseup = () => {
    if (isDragging) {
      setIsDragging(false)
    }
  }

  const handleThumbMousemove = (e: MouseEvent) => {
    if (isDragging) {
      e.preventDefault()
      e.stopPropagation()
      if (
        scrollStartPosition !== null &&
        contentRef.current &&
        scrollTrackRef.current
      ) {
        const deltaY = (e.clientY - scrollStartPosition) * (contentRef.current.scrollHeight / scrollTrackRef.current.clientHeight)
        contentRef.current.scrollTop = initialScrollTop + deltaY
      }
    }
  }

  useEffect(() => {
    if (contentRef.current && scrollTrackRef.current) {
      const ref = contentRef.current
      const { clientHeight: trackSize } = scrollTrackRef.current
      observer.current = new ResizeObserver(() => {
        handleResize(ref, trackSize)
      })
      observer.current.observe(ref)
      ref.addEventListener('scroll', handleThumbPosition)
      return () => {
        observer.current?.unobserve(ref)
        ref.removeEventListener('scroll', handleThumbPosition)
      }
    }
  }, [])

  useEffect(() => {
    document.addEventListener('mousemove', handleThumbMousemove)
    document.addEventListener('mouseup', handleThumbMouseup)
    document.addEventListener('mouseleave', handleThumbMouseup)
    return () => {
      document.removeEventListener('mousemove', handleThumbMousemove)
      document.removeEventListener('mouseup', handleThumbMouseup)
      document.removeEventListener('mouseleave', handleThumbMouseup)
    }
  }, [isDragging])

  return (
    <div className={`relative overflow-hidden ${className}`}>
      <div
        ref={contentRef}
        className="h-full overflow-y-scroll scrollbar-hide"
        style={{ marginRight: '-20px', paddingRight: '20px' }}
      >
        {children}
      </div>
      <div className="absolute right-0 top-0 bottom-0 w-2 transition-opacity">
        <div
          ref={scrollTrackRef}
          className="absolute top-0 right-0 bottom-0 w-full cursor-pointer"
          onClick={handleTrackClick}
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.1)' }}
        >
          <div
            ref={scrollThumbRef}
            className="absolute w-full rounded transition-opacity"
            style={{
              height: `${thumbHeight}px`,
              backgroundColor: 'rgba(0, 0, 0, 0.4)',
              top: 0,
            }}
            onMouseDown={handleThumbMousedown}
          />
        </div>
      </div>
    </div>
  )
}