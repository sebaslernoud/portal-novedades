// Campos de formulario con etiqueta, marca de obligatorio y error del backend.
// Fechas y horas usan los selectores nativos: no se pueden escribir formatos inválidos.
import { CircleAlert } from 'lucide-react';
import { useId, type ReactNode } from 'react';

type PropsBase = {
  etiqueta: string;
  error?: string;
  obligatorio?: boolean;
  ayuda?: string;
};

// El texto " *" forma parte de la etiqueta visible; los lectores de pantalla usan `required`.
export const MarcaObligatorio = () => (
  <span className="obligatorio" aria-hidden="true">
    {' *'}
  </span>
);

export function ErrorCampo({ id, children }: { id?: string; children: ReactNode }) {
  return (
    <small id={id} className="error-campo" role="alert">
      <CircleAlert aria-hidden="true" size={14} />
      {children}
    </small>
  );
}

function Envoltorio({ id, etiqueta, error, obligatorio, ayuda, children }: PropsBase & { id: string; children: ReactNode }) {
  return (
    <div className={`campo${error ? ' campo-con-error' : ''}`}>
      <label htmlFor={id}>
        {etiqueta}
        {obligatorio && <MarcaObligatorio />}
      </label>
      {children}
      {ayuda && (
        <small id={`${id}-ayuda`} className="ayuda">
          {ayuda}
        </small>
      )}
      {error && <ErrorCampo id={`${id}-error`}>{error}</ErrorCampo>}
    </div>
  );
}

function atributos(id: string, { error, obligatorio, ayuda }: PropsBase) {
  const describe = [ayuda && `${id}-ayuda`, error && `${id}-error`].filter(Boolean).join(' ');
  return {
    id,
    required: obligatorio,
    'aria-invalid': error ? true : undefined,
    'aria-describedby': describe || undefined,
  };
}

type PropsEntrada = PropsBase & { valor: string; alCambiar: (valor: string) => void };

function Entrada({ tipo, ...props }: PropsEntrada & { tipo: 'date' | 'time' | 'text' }) {
  const id = useId();
  return (
    <Envoltorio id={id} {...props}>
      <input
        type={tipo}
        value={props.valor}
        onChange={(e) => props.alCambiar(e.target.value)}
        {...atributos(id, props)}
      />
    </Envoltorio>
  );
}

export const CampoFecha = (props: PropsEntrada) => <Entrada tipo="date" {...props} />;

export const CampoHora = (props: PropsEntrada) => <Entrada tipo="time" {...props} />;

export function CampoTexto({ multilinea, maximo = 500, ...props }: PropsEntrada & { multilinea?: boolean; maximo?: number }) {
  const id = useId();
  const comunes = { value: props.valor, maxLength: maximo, ...atributos(id, props) };
  return (
    <Envoltorio id={id} {...props}>
      {multilinea ? (
        <textarea rows={3} onChange={(e) => props.alCambiar(e.target.value)} {...comunes} />
      ) : (
        <input type="text" onChange={(e) => props.alCambiar(e.target.value)} {...comunes} />
      )}
    </Envoltorio>
  );
}

type PropsSelector = PropsEntrada & { opciones: { valor: string; nombre: string }[] };

export function CampoSelector({ opciones, ...props }: PropsSelector) {
  const id = useId();
  return (
    <Envoltorio id={id} {...props}>
      <select value={props.valor} onChange={(e) => props.alCambiar(e.target.value)} {...atributos(id, props)}>
        <option value="">Elegí una opción</option>
        {opciones.map((o) => (
          <option key={o.valor} value={o.valor}>
            {o.nombre}
          </option>
        ))}
      </select>
    </Envoltorio>
  );
}

// `destacado`: título y opciones más grandes, para elecciones que definen el resto del formulario.
export function CampoOpciones({ opciones, destacado, ...props }: PropsSelector & { destacado?: boolean }) {
  const nombre = useId();
  const clases = ['campo', destacado && 'campo-opciones-destacado', props.error && 'campo-con-error'];
  return (
    <fieldset className={clases.filter(Boolean).join(' ')} aria-required={props.obligatorio}>
      <legend>
        {props.etiqueta}
        {props.obligatorio && <MarcaObligatorio />}
      </legend>
      <div className="opciones">
        {opciones.map((o) => (
          <label key={o.valor} className="opcion">
            <input
              type="radio"
              name={nombre}
              value={o.valor}
              checked={props.valor === o.valor}
              required={props.obligatorio}
              onChange={() => props.alCambiar(o.valor)}
            />
            {o.nombre}
          </label>
        ))}
      </div>
      {props.error && <ErrorCampo>{props.error}</ErrorCampo>}
    </fieldset>
  );
}
