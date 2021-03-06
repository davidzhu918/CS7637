# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.

from PIL import Image, ImageChops, ImageOps, ImageStat, ImageDraw
from Figure import Figure
from Object import Object

class Agent:
    attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']
    sizes_list = ['very small', 'small', 'medium', 'large', 'very large', 'huge']  # index = size value
    transforms_list = ['nothing']
    points_attribute = 1
    points_pattern = 2

    threshold = .98
    points_holistic_symmetry = 5
    points_bonus = 1

    figure_a = []
    figure_b = []
    figure_c = []
    figure_d = []
    figure_e = []
    figure_f = []
    figure_g = []
    figure_h = []
    figure_sol = []
    solutions = []

    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    def is_equal(self, im1, im2):
        val = self.get_similarity(im1, im2)
        return val > self.threshold

    def get_similarity(self, im1, im2):
        max_similarity = 0
        for x_offset in range(-3, 4, 1):
            for y_offset in range(-3, 4, 1):
                diff = ImageChops.difference(ImageChops.offset(im1, x_offset, y_offset), im2)
                num_pixels = im2.size[0] * im1.size[1]
                diff_stats = ImageStat.Stat(diff)
                similarity = 1.0 - ((diff_stats.sum[0] / 255) / num_pixels)
                max_similarity = max(similarity, max_similarity)
        return max_similarity


    def translate_object(self, obj, distance):
        obj_new = Object((0, 0), 0)
        obj_new.remove_pixel((0, 0))

        for xy in obj.area:
            obj_new.add_pixel((xy[0] + distance[0], xy[1] + distance[1]))

        obj_new.find_centroid()
        return obj_new

    def image_from_objects(self, size, objects):
        image = Image.new('L', size, color=255)
        for obj in objects:
            for xy in obj.area:
                try:
                    image.putpixel(xy, 0)
                except IndexError:
                    pass

        return image

    def horizontal_pass_through(self, figure1, figure2, figure3):
        im = figure1.image
        size = im.size
        im_centroid = (size[0]/2, size[1]/2)
        max_distance = size[0]/2 - 1

        for i in xrange(0, max_distance, 2):
            objects_new = []

            for j in xrange(1, len(figure1.objects), 1):
                obj = figure1.objects[j]

                # Only interested in dark objects whose centroids are not in the center of the image
                if obj.l_val < 128 and abs(obj.centroid[0] - im_centroid[0]) > 3:
                    # On the left side
                    if obj.centroid[0] < im_centroid[0]:
                        obj_new = self.translate_object(obj, (i, 0))
                    # On the right side
                    else:
                        obj_new = self.translate_object(obj, (-i, 0))

                    objects_new.append(obj_new)
            # end of loop

            im_new = self.image_from_objects(size, objects_new)

            # If equal, we know this is the transform
            if self.is_equal(im_new, figure2.image):
                return ['horizontal pass through']

        return ['NOT horizontal pass through']

    def get_transform(self, figure1, figure2, figure3):

        figure1.identify_objects()
        figure2.identify_objects()
        figure3.identify_objects()
        figure1.find_centroids()
        figure2.find_centroids()
        figure3.find_centroids()

        '''
        *** TEST CODE ***
        # Take difference of images and show result
        fig_diff = Figure(ImageChops.difference(figure1.image, figure2.image))
        fig_diff.identify_objects()
        fig_diff.image.show()
        '''

        # Check for resizing
        if len(figure1.objects) == len(figure2.objects) == len(figure3.objects) == 2:
            # Check for simple shape resize
            obj1 = figure1.objects[1]
            obj2 = figure2.objects[1]
            obj3 = figure3.objects[1]

            obj1_size = obj1.size()
            obj2_size = obj2.size()
            obj3_size = obj3.size()

            xy_diff_23 = (obj3_size[0] - obj2_size[0], obj3_size[1] - obj2_size[1])
            xy_diff_12 = (obj2_size[0] - obj1_size[0], obj2_size[1] - obj1_size[1])

            if abs(xy_diff_23[0] - xy_diff_12[0]) < 3 and abs(xy_diff_23[1] - xy_diff_12[1]) < 3:
                resize_amount = ((xy_diff_23[0] + xy_diff_12[0]) / 2, (xy_diff_23[1] + xy_diff_12[1]) / 2)
                return ['resize', resize_amount]

        if len(figure1.objects) >= 2:
            # Check for Add + Horizontal Slide
            obj1 = figure1.objects[1]
            size = figure1.image.size
            width_image = size[0]
            width_obj = obj1.size()[0]
            max_slide_distance = (width_image / 2) - (width_obj / 2)

            for i in xrange(0, max_slide_distance, 2):
                init_l_val = 255
                obj1_new = Object((0, 0), 0)
                obj2_new = Object((0, 0), 0)
                obj1_new.remove_pixel((0, 0))
                obj2_new.remove_pixel((0, 0))

                # Slide first two objects away from each other
                for coord in obj1.area:
                    obj1_new.add_pixel((coord[0] + i, coord[1]))
                    obj2_new.add_pixel((coord[0] - i, coord[1]))
                image_new = Image.new('L', size, color=init_l_val)

                # Make new image with translated objects
                try:
                    for xy in obj1_new.area:
                        image_new.putpixel(xy, 0)
                    for xy in obj2_new.area:
                        image_new.putpixel(xy, 0)
                except IndexError:
                    break

                # Check if it is correct
                if self.is_equal(image_new, figure2.image):
                    image_new = Image.new('L', size, color=init_l_val)

                    # Translate objects again
                    for xy in obj1_new.area:
                        image_new.putpixel((xy[0] + i, xy[1]), 0)
                    for xy in obj2_new.area:
                        image_new.putpixel((xy[0] - i, xy[1]), 0)
                    # Add third object
                    for xy in obj1.area:
                        image_new.putpixel(xy, 0)

                    # Check that transformation propagates to 3rd figure
                    if self.is_equal(image_new, figure3.image):
                        slide_distance = i
                        return ['add and translate', slide_distance]

        # Check for Horizontal Pass Through
        result = self.horizontal_pass_through(figure1, figure2, figure3)
        if result[0] == 'horizontal pass through':
            return result

        return ['no transform found']

    #Merged all figures in problem + solution into a single large image
    def create_merged_image(self):
        x_orig = self.figure_a.image.size[0]
        y_orig = self.figure_a.image.size[1]
        x_new = x_orig * 3
        y_new = y_orig * 3
        merged_img = Image.new('L', (x_new, y_new))

        x = 0
        y = 0
        merged_img.paste(self.figure_a.image, (x, y))
        x += x_orig
        merged_img.paste(self.figure_b.image, (x, y))
        x += x_orig
        merged_img.paste(self.figure_c.image, (x, y))

        x = 0
        y += y_orig
        merged_img.paste(self.figure_d.image, (x, y))
        x += x_orig
        merged_img.paste(self.figure_e.image, (x, y))
        x += x_orig
        merged_img.paste(self.figure_f.image, (x, y))

        x = 0
        y += y_orig
        merged_img.paste(self.figure_g.image, (x, y))
        x += x_orig
        merged_img.paste(self.figure_h.image, (x, y))
        x += x_orig
        merged_img.paste(self.figure_sol.image, (x, y))

        return merged_img

    #Checks for vertical symmetry (across vertical axis)
    def get_vertical_symmetry_measure(self, image):
        return self.get_similarity(image, ImageOps.mirror(image))

    #Checks for horizontal symmetry (across horiontal axis)
    def get_horizontal_symmetry_measure(self, image):
        return self.get_similarity(image, ImageOps.flip(image))

    def find_most_similar_solution(self, fig):
        similarity_scores = []
        for solution in self.solutions:
            similarity_scores.append(self.get_similarity(fig.image, solution.image))
        return similarity_scores.index(max(similarity_scores)) + 1

    def get_solution(self):
        answer = -1


        # *** REAL CODE ***
        # Check for holistic symmetry
        vertical_symmetry_measures = []
        horizontal_symmetry_measures = []
        for solution in self.solutions:
            self.figure_sol = solution
            holistic_image = self.create_merged_image()
            vertical_symmetry_measures.append(self.get_vertical_symmetry_measure(holistic_image))
            horizontal_symmetry_measures.append(self.get_horizontal_symmetry_measure(holistic_image))
        # Check vertical
        max_measure = max(vertical_symmetry_measures)
        if max_measure > self.threshold:
            return vertical_symmetry_measures.index(max_measure) + 1
        # Check horizontal
        max_measure = max(horizontal_symmetry_measures)
        if max_measure > self.threshold:
            return horizontal_symmetry_measures.index(max_measure) + 1


        # Horizontal transforms alone have been sufficient for the practice problems encountered
        transform = self.get_transform(self.figure_a, self.figure_b, self.figure_c)

        # These values used later on
        self.figure_g.identify_objects()
        self.figure_g.find_centroids()
        self.figure_h.identify_objects()
        self.figure_h.find_centroids()

        if transform[0] == 'resize':
            # if at this point, only 2 objects in figure
            # Get size of object in question and get scale factor from transform data
            obj = self.figure_h.objects[1]
            width_obj, height_obj = obj.size()
            width_trans, height_trans = transform[1]
            scale = (1 + width_trans / float(width_obj), 1 + height_trans / float(height_obj))

            im = self.figure_h.image
            width, height = im.size
            im_resized = im.resize((int(width * scale[0]), int(height * scale[1])), Image.BILINEAR)
            width_new, height_new = im_resized.size
            width_diff = width_new - width
            height_diff = height_new - height
            box = (width_diff/2, height_diff/2, width_new - width_diff/2, height_new - height_diff/2)
            fig = Figure(im_resized.crop(box))
            answer = self.find_most_similar_solution(fig)

        elif transform[0] == 'add and translate':
            translate_distance = transform[1]
            obj1 = self.figure_g.objects[1]
            size = self.figure_g.image.size

            init_l_val = 255
            obj1_new = Object((0, 0), 0)
            obj2_new = Object((0, 0), 0)
            obj1_new.remove_pixel((0, 0))
            obj2_new.remove_pixel((0, 0))

            # Slide first two objects away from each other
            for coord in obj1.area:
                obj1_new.add_pixel((coord[0] + translate_distance*2, coord[1]))
                obj2_new.add_pixel((coord[0] - translate_distance*2, coord[1]))

            # Make new image with translated objects
            image_new = Image.new('L', size, color=init_l_val)
            for xy in obj1_new.area:
                image_new.putpixel(xy, 0)
            for xy in obj2_new.area:
                image_new.putpixel(xy, 0)
            for xy in obj1.area:
                image_new.putpixel(xy, 0)

            fig = Figure(image_new)
            answer = self.find_most_similar_solution(fig)

        elif transform[0] == 'horizontal pass through':
            for solution in self.solutions:
                solution.identify_objects()
                num_dark_obj = 0
                for obj in solution.objects:
                    if obj.l_val < 128:
                        num_dark_obj += 1
                if num_dark_obj < 2:
                    continue

                size = solution.image.size
                im_centroid = (size[0]/2, size[1]/2)
                max_distance = size[0]/2
                for i in xrange(2, max_distance, 2):
                    objects_new = []
                    for obj in solution.objects:
                        if obj.l_val < 128:
                            # On the left side
                            if obj.centroid[0] < im_centroid[0]:
                                obj_new = self.translate_object(obj, (i, 0))
                            # On the right side
                            else:
                                obj_new = self.translate_object(obj, (-i, 0))

                            objects_new.append(obj_new)
                    image_new = self.image_from_objects(size, objects_new)
                    if self.is_equal(image_new, solution.image):
                        answer = self.solutions.index(solution) + 1
                        return answer

        return answer

    def Solve(self, problem):
        print problem.name
        problem_name = problem.name
        answer = -1
        scores = []

        #Load all figures and make them black OR white (no grey!)
        self.figure_a = Figure(problem.figures['A'].visualFilename)
        self.figure_b = Figure(problem.figures['B'].visualFilename)
        self.figure_c = Figure(problem.figures['C'].visualFilename)
        self.figure_d = Figure(problem.figures['D'].visualFilename)
        self.figure_e = Figure(problem.figures['E'].visualFilename)
        self.figure_f = Figure(problem.figures['F'].visualFilename)
        self.figure_g = Figure(problem.figures['G'].visualFilename)
        self.figure_h = Figure(problem.figures['H'].visualFilename)
        self.solutions = []
        problem_figure_keys = sorted(problem.figures.keys())
        num_solutions = 8
        for i in range(num_solutions):
            figure_sol = Figure(problem.figures[problem_figure_keys[i]].visualFilename)
            self.solutions.append(figure_sol)

        answer = self.get_solution()

        '''
        print problem.name
        print "Scores :", scores
        print "Correct answer: ", problem.correctAnswer
        print "Answer selected: ", answer, '\n'
        '''
        return answer



