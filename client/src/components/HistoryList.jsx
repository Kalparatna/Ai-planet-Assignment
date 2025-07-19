export default function HistoryList({ history, onSelect }) {
    return (
      <div className="mt-8">
        <h2 className="text-lg font-medium">Recent Queries</h2>
        <ul className="mt-2 divide-y border rounded">
          {history.map((item) => (
            <li
              key={item.id}
              onClick={() => onSelect(item)}
              className="p-3 hover:bg-gray-50 cursor-pointer"
            >
              <p className="text-sm text-gray-800">{item.query}</p>
              <p className="text-xs text-gray-500">
                {new Date(item.timestamp).toLocaleString()}
              </p>
            </li>
          ))}
        </ul>
      </div>
    );
  }
  