type Props = { className?: string };

/**
 * Marca del obelisco. SVG en linea a proposito: hereda el color del texto, se anima
 * con CSS y no depende de un archivo que haya que resolver distinto en dev y en build.
 */
export default function LogoObelisco({ className }: Props) {
  return (
    <svg
      className={className}
      viewBox="0 0 120 200"
      role="img"
      aria-label="Obelisco"
      fill="none"
      stroke="currentColor"
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      {/* Base */}
      <path d="M18 178h84v14H18z" fill="currentColor" fillOpacity="0.14" strokeWidth="2" />
      {/* Fuste, con la inclinacion del obelisco */}
      <path
        d="M44 40h32l-6 138H50z"
        fill="currentColor"
        fillOpacity="0.08"
        strokeWidth="2.5"
      />
      {/* Piramidion */}
      <path
        d="M44 40 60 12l16 28z"
        fill="currentColor"
        fillOpacity="0.18"
        strokeWidth="2.5"
      />
      {/* Junta central: la linea que da verticalidad */}
      <path d="M60 12v166" strokeWidth="1" strokeOpacity="0.4" />
      {/* Arista de luz */}
      <path d="M52 46 56 172" strokeWidth="1" strokeOpacity="0.25" />
    </svg>
  );
}
