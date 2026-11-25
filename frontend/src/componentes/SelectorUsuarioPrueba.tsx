import { UserRound } from 'lucide-react';
import { useUsuario } from '../contexto/Usuario';

export default function SelectorUsuarioPrueba() {
  const { usuario, personas, elegir } = useUsuario();
  return (
    <div className="usuario-prueba">
      <span className="marca-prueba">Modo prueba</span>
      <label className="selector-usuario">
        <UserRound aria-hidden="true" size={18} />
        <span className="solo-lectores">Usuario</span>
        <select
          value={usuario?.legajo ?? ''}
          onChange={(e) => elegir(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">Elegí un usuario</option>
          {personas.map((p) => (
            <option key={p.legajo} value={p.legajo}>
              {p.nombre} · {p.roles.includes('rrhh') ? 'RR.HH.' : p.roles.includes('jefe') ? 'Jefe' : 'Empleado'}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
