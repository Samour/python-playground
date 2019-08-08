import json
import model
import generator


class IPuzzleSerializer:

  def serialize(self, puzzle):
    pass

  def deserialize(self, data):
    pass


class PuzzleStatementSerializer(IPuzzleSerializer):

  def serialize(self, puzzle):
    return json.dumps({
      'model': puzzle.model,
      'size': puzzle.size,
      'line_counts': [self._map_line_count(count) for count in puzzle.line_counts]
    })

  def _map_line_count(self, line_count):
    return {
      'vertex': self._map_vertex(line_count.vertex),
      'value': line_count.value
    }

  def _map_vertex(self, vertex):
    return {
      'x': vertex.x,
      'y': vertex.y
    }

  def deserialize(self, data):
    data_model = json.loads(data)
    if data_model['model'] == model.Puzzle.MODEL_GRID:
      puzzle = generator.grid(data_model['size'][0], data_model['size'][1])
    else:
      raise Exception('Could not deserialize model')
    line_counts = [self._unmap_line_count(count) for count in data_model['line_counts']]
    for count in map(self._unmap_line_count, data_model['line_counts']):
      for line_count in puzzle.line_counts:
        if line_count.vertex.x == count.vertex.x and line_count.vertex.y == count.vertex.y:
          line_count.value = count.value
          continue

    return puzzle

  def _unmap_line_count(self, count):
    return model.LineCount(self._unmap_vertex(count['vertex']), count['value'])

  def _unmap_vertex(self, vertex):
    return model.Vertex(vertex['x'], vertex['y'])
